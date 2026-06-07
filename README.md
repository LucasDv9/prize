# Prize Sniper Hub 🎯

Um gerenciador de abas automático com interface web, desenvolvido em Python com Playwright e Flask.

## Características

✅ **Login automático** - Sem necessidade de keys  
✅ **Gerenciamento de abas** - Abra e feche abas com facilidade  
✅ **Suporte a proxy** - Configure proxy por aba  
✅ **Interface web moderna** - Dashboard intuitivo em português  
✅ **Monitoramento** - Monitore abas em tempo real  
✅ **Auto-atualização** - Sistema de updates integrado  

## Requisitos

- Python 3.8+
- Navegador Chromium (instalado automaticamente pelo Playwright)

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/LucasDv9/prize.git
cd prize
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Instale o Chromium (primeira execução)

```bash
playwright install chromium
```

## Uso

### Executar com Interface Gráfica

```bash
python hub.py
```

Isso irá:
1. Iniciar o servidor Flask em `http://127.0.0.1:5000`
2. Abrir automaticamente o navegador com a interface do Hub
3. Fazer login automático sem necessidade de keys

### Executar em Modo Headless (sem interface gráfica)

```bash
python hub.py --headless
```

Útil para servidores ou execução em background.

## Estrutura do Projeto

```
prize/
├── hub.py                 # Aplicação principal (backend)
├── templates/
│   └── hub.html          # Interface web (frontend)
├── requirements.txt      # Dependências Python
└── README.md            # Este arquivo
```

## Como Funciona

### Backend (hub.py)

O arquivo `hub.py` contém:

- **HubBridge**: Gerencia a comunicação entre frontend e Playwright
  - `login_direct()` - Login automático sem keys
  - `open_tab()` - Abre nova aba com URL e proxy opcional
  - `close_tab()` - Fecha uma aba
  - `logout()` - Faz logout e limpa recursos
  - `check_update()` - Verifica atualizações
  - `apply_update()` - Aplica atualizações

- **HubApp**: Servidor Flask que serve a interface
  - Rota `/` - Serve o `hub.html`
  - Rota `/api/status` - Retorna status do app

### Frontend (templates/hub.html)

Interface web com:
- Login automático
- Gerenciamento de abas
- Configuração de proxy
- Monitoramento de página
- Sistema de updates
- Suporte a modo admin

## API Bridge

A comunicação entre JavaScript e Python acontece via `window._hubBridge()`:

```javascript
// Login automático
const result = await window._hubBridge('loginDirect', {});

// Abrir aba
const result = await window._hubBridge('openTab', {
  tabId: 'tab-123',
  url: 'https://example.com',
  proxy: '192.168.1.1:8080',
  monitor: true
});

// Fechar aba
const result = await window._hubBridge('closeTab', {
  tabId: 'tab-123'
});

// Logout
const result = await window._hubBridge('logout', {});
```

## Configurações

### Modificar máximo de slots

No `hub.py`, na função `login_direct()`:

```python
self.current_user = {
    "user": "guest",
    "max_slots": 10,  # Altere este valor
    ...
}
```

### Adicionar plataformas pré-configuradas

No `templates/hub.html`, na seção do formulário modal:

```html
<select id="modal-platform" class="form-select">
    <option value="https://www.nike.com">Nike</option>
    <option value="https://www.adidas.com">Adidas</option>
    <!-- Adicione mais aqui -->
</select>
```

## Troubleshooting

### "Bridge não disponível"

Isso significa que o JavaScript não conseguiu se conectar ao Python. Tente:

1. Verificar se o servidor Flask está rodando
2. Fechar e abrir o app novamente
3. Verificar logs no terminal

### Proxy não funciona

Certifique-se de usar o formato correto:
- `ip:porta` - `192.168.1.1:8080`
- `ip:porta:usuario:senha` - `192.168.1.1:8080:admin:pass`

### Abas não abrem

1. Verifique se o Chromium foi instalado: `playwright install chromium`
2. Verifique se a URL é válida
3. Verifique logs no terminal para mais detalhes

## Logs

Os logs são exibidos no terminal com o formato:

```
2026-06-07 00:00:00 - prize-hub - INFO - Tab opened: tab-123 - https://example.com
```

Para mais detalhes de debug, você pode ajustar o nível de log em `hub.py`:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Modo Admin

Para ativar modo admin, modifique a função `get_hwid()` em `hub.py`:

```python
return {
    ...
    "admin": True,  # Altere para True
}
```

## Segurança

⚠️ **Importante:**
- Este projeto não inclui autenticação segura de produção
- Não use em ambientes públicos ou não confiáveis
- O modo admin deve ser desativado em produção

## Extensões Futuras

Ideias para melhorias:

- [ ] Banco de dados para persistir abas
- [ ] Sistema de eventos com WebSocket
- [ ] Captura de screenshots das abas
- [ ] Integração com APIs externas
- [ ] Sistema de agendamento
- [ ] Autenticação segura com tokens

## Contribuindo

Sinta-se livre para abrir issues e pull requests!

## Licença

Este projeto é fornecido como está, sem garantias.

## Contato

GitHub: [@LucasDv9](https://github.com/LucasDv9)

---

**Desenvolvido com ❤️ em Python**
