"""
Prize Sniper Hub - Main Application
Manages browser automation with Playwright and provides Hub UI via Flask
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List

from flask import Flask, render_template, jsonify
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("prize-hub")


class HubBridge:
    """Handles all communication between JavaScript frontend and Python backend."""
    
    def __init__(self):
        self.current_user: Optional[Dict] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pages: Dict[str, Page] = {}
        self.app_version = "1.0.0"
        self.config_dir = Path.home() / ".prize-hub"
        self.config_dir.mkdir(exist_ok=True)
        logger.info(f"HubBridge initialized. Config dir: {self.config_dir}")
    
    async def initialize_browser(self):
        """Initialize Playwright browser."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def get_hwid(self) -> Dict:
        """Return hardware ID, version, and admin status."""
        hwid = str(uuid.getnode())[:16]
        return {
            "ok": True,
            "hwid": hwid,
            "version": self.app_version,
            "admin": False,
            "savedKey": None
        }
    
    async def login_direct(self) -> Dict:
        """
        Direct login without key validation.
        Returns user info with default settings.
        """
        try:
            # Create default user session
            self.current_user = {
                "user": "guest",
                "max_slots": 10,
                "expires_at": None,  # No expiration
                "created_at": datetime.now().isoformat(),
                "session_id": str(uuid.uuid4())
            }
            
            logger.info(f"User logged in: {self.current_user['user']}")
            
            return {
                "ok": True,
                "user": self.current_user["user"],
                "max_slots": self.current_user["max_slots"],
                "expires_at": self.current_user["expires_at"],
                "session_id": self.current_user["session_id"]
            }
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {
                "ok": False,
                "error": str(e)
            }
    
    async def logout(self) -> Dict:
        """Logout and cleanup resources."""
        try:
            # Close all pages
            for tab_id, page in list(self.pages.items()):
                try:
                    await page.close()
                except:
                    pass
            self.pages.clear()
            
            self.current_user = None
            logger.info("User logged out")
            
            return {"ok": True}
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return {
                "ok": False,
                "error": str(e)
            }
    
    async def open_tab(self, tab_id: str, url: str, proxy: Optional[str] = None, monitor: bool = False) -> Dict:
        """
        Open a new tab/page with the given URL.
        
        Args:
            tab_id: Unique identifier for the tab
            url: URL to navigate to
            proxy: Optional proxy URL
            monitor: Whether to enable monitoring
        """
        try:
            if not self.current_user:
                return {
                    "ok": False,
                    "error": "Not authenticated"
                }
            
            if len(self.pages) >= self.current_user["max_slots"]:
                return {
                    "ok": False,
                    "error": f"Reached maximum slots ({self.current_user['max_slots']})"
                }
            
            if not self.context:
                await self.initialize_browser()
            
            # Create proxy context if provided
            context = self.context
            if proxy:
                context = await self.browser.new_context(
                    proxy={"server": proxy}
                )
            
            # Create new page
            page = await context.new_page()
            
            # Navigate to URL
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                logger.warning(f"Navigation timeout or error: {e}")
                # Still consider it success if page exists
            
            # Get page title
            title = await page.title()
            if not title:
                title = self._extract_host_from_url(url)
            
            # Store page reference
            self.pages[tab_id] = page
            
            logger.info(f"Tab opened: {tab_id} - {url}")
            
            return {
                "ok": True,
                "tab_id": tab_id,
                "title": title,
                "url": url
            }
        except Exception as e:
            logger.error(f"Failed to open tab {tab_id}: {e}")
            return {
                "ok": False,
                "error": str(e)
            }
    
    async def close_tab(self, tab_id: str) -> Dict:
        """Close a tab."""
        try:
            if tab_id in self.pages:
                page = self.pages[tab_id]
                await page.close()
                del self.pages[tab_id]
                logger.info(f"Tab closed: {tab_id}")
            
            return {"ok": True}
        except Exception as e:
            logger.error(f"Failed to close tab {tab_id}: {e}")
            return {
                "ok": False,
                "error": str(e)
            }
    
    async def check_update(self) -> Dict:
        """Check for application updates."""
        # Placeholder - implement your update check logic
        return {
            "ok": True,
            "has_update": False,
            "latest": None,
            "notes": None,
            "auto_apply": False
        }
    
    async def apply_update(self, version: str) -> Dict:
        """Apply an update."""
        # Placeholder - implement your update logic
        try:
            logger.info(f"Applying update: {version}")
            return {"ok": True}
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return {
                "ok": False,
                "error": str(e)
            }
    
    @staticmethod
    def _extract_host_from_url(url: str) -> str:
        """Extract hostname from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc or url
        except:
            return url
    
    async def handle_request(self, method: str, params: Dict) -> Dict:
        """
        Central router for all frontend requests.
        
        Args:
            method: Method name to call
            params: Parameters for the method
        """
        handlers = {
            "getHwid": lambda: self.get_hwid(),
            "loginDirect": lambda: self.login_direct(),
            "logout": lambda: self.logout(),
            "openTab": lambda: self.open_tab(
                params.get("tabId"),
                params.get("url"),
                params.get("proxy"),
                params.get("monitor", False)
            ),
            "closeTab": lambda: self.close_tab(params.get("tabId")),
            "checkUpdate": lambda: self.check_update(),
            "applyUpdate": lambda: self.apply_update(params.get("version")),
        }
        
        if method not in handlers:
            logger.warning(f"Unknown method: {method}")
            return {
                "ok": False,
                "error": f"Method '{method}' not found"
            }
        
        try:
            handler = handlers[method]
            result = handler()
            
            # Handle async results
            if asyncio.iscoroutine(result):
                result = await result
            
            return result
        except Exception as e:
            logger.error(f"Error handling {method}: {e}")
            return {
                "ok": False,
                "error": str(e)
            }


class HubApp:
    """Main application class."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.bridge = HubBridge()
        self._setup_routes()
        logger.info("HubApp initialized")
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route("/")
        def index():
            """Serve the Hub UI."""
            return render_template("hub.html")
        
        @self.app.route("/api/status")
        def status():
            """Return app status."""
            return jsonify({
                "status": "running",
                "version": self.bridge.app_version,
                "user": self.bridge.current_user
            })
    
    async def run_with_playwright(self, host: str = "127.0.0.1", port: int = 5000):
        """
        Run Flask app with Playwright integration.
        
        Uses Playwright to open the Hub UI automatically.
        """
        try:
            await self.bridge.initialize_browser()
            
            # Start Flask in a background thread
            import threading
            flask_thread = threading.Thread(
                target=lambda: self.app.run(host=host, port=port, debug=False),
                daemon=True
            )
            flask_thread.start()
            
            # Wait for Flask to start
            await asyncio.sleep(2)
            
            # Open Hub UI in browser
            page = await self.bridge.context.new_page()
            await page.goto(f"http://{host}:{port}/", wait_until="domcontentloaded")
            
            # Expose the bridge to JavaScript
            async def bridge_handler(method: str, params: Dict) -> Dict:
                return await self.bridge.handle_request(method, params)
            
            await page.expose_function("_hubBridge", bridge_handler)
            
            logger.info(f"Hub running at http://{host}:{port}")
            logger.info("Press Ctrl+C to stop")
            
            # Keep the app running
            while True:
                await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            if self.bridge.browser:
                await self.bridge.browser.close()
        except Exception as e:
            logger.error(f"Error running app: {e}")
            raise
    
    async def run_headless(self, host: str = "127.0.0.1", port: int = 5000):
        """
        Run Flask app in headless mode (no browser UI).
        Useful for server deployments.
        """
        try:
            await self.bridge.initialize_browser()
            
            import threading
            flask_thread = threading.Thread(
                target=lambda: self.app.run(host=host, port=port, debug=False),
                daemon=True
            )
            flask_thread.start()
            
            logger.info(f"Hub running (headless) at http://{host}:{port}")
            logger.info("Press Ctrl+C to stop")
            
            while True:
                await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            if self.bridge.browser:
                await self.bridge.browser.close()
        except Exception as e:
            logger.error(f"Error running app: {e}")
            raise


def main():
    """Main entry point."""
    import sys
    
    # Determine whether to run with browser UI or headless
    headless = "--headless" in sys.argv
    
    app = HubApp()
    
    try:
        if headless:
            asyncio.run(app.run_headless())
        else:
            asyncio.run(app.run_with_playwright())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
