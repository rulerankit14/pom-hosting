# PX9V Landing Provisioner — updated template

This package contains a Telegram landing/store bot that provisions isolated PX9V bot instances from the supplied `9V-main.zip` template.

## Landing flow

`/start` → **BUY NEW BOT** → send access/create key → send customer bot token → send Admin ID → bot is provisioned and started.

If the access key was created with Premium enabled, the new PX9V instance receives a one-time PX9V-compatible Premium Key. The key uses the same `premium_keys` schema and redemption flow as the supplied PX9V source.

## Admin

`/admin` opens the landing admin panel.

**CREATE TOKEN** asks for:
1. USER / bot-creation count
2. Whether a Premium Key should be included
3. Premium KEY USER limit
4. Premium KEY REVENUE limit
5. Premium KEY TIME in days

The access key can therefore provision exactly the configured number of customer bots.

## Revoke

A customer can revoke their own bot with:

- `/revoke @botusername`
- `/revoke ACCESS_TOKEN`

Revoking an access token also revokes/stops every bot created from that access token.

The landing admin can revoke any bot/token.

## Important environment variables

```text
LANDING_BOT_TOKEN=...
LANDING_ADMIN_ID=...
LANDING_DB_PATH=/data/landing_bot.db
INSTANCE_ROOT=/data/instances
TEMPLATE_ROOT=px9v_template
MASTER_INSTANCE_KEY=<44-character URL-safe Fernet key>
REVOKE_DELETE_FILES=true
```

Generate `MASTER_INSTANCE_KEY` without installing cryptography on the phone:

```bash
python -c "import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

## Railway

Add a Railway Volume mounted at `/data`. This keeps the landing DB and customer bot instances across redeployments.

Start command:

```text
python main.py
```

## PX9V template / QR handling

The customer bot template is the newly supplied `9V-main.zip`, not the previous template.

Its `requirements.txt` includes `qrcode[pil]>=8.0`. Additionally, the QR code handler has an HTTP QR fallback, so the customer bot does not show the old `QR module is missing on the server` error merely because the optional local QR package is unavailable.


## PX9V template authorization gate

The `px9v_template` bot now includes a local authorization gate that runs before
existing command and callback handlers. Existing bot features remain unchanged
after authorization.

- The developer allowlist is fixed inside `px9v_template/security_guard.py` as
  hashed Telegram IDs; there is no developer-ID environment variable.
- On first use, the bot remains locked until an approved developer sends
  `/authorize <code>`. The initial code supplied for this build is `Mridul.xxx`.
- `/block` is available only to one of the two fixed approved developer accounts.
  It persists across restarts. To unlock, an approved developer uses
  `/authorize <code>` again.
- Approval and block status are stored in `authorization_state.sqlite3` beside
  the template's `main.py`.

### Important security limitation

This gate helps protect the unmodified package from ordinary users and casual
configuration changes. Because customers receive the Python source and control
their hosting machine, they can still modify code or local database state.
Hashed IDs and code obfuscation are not tamper-proof. Without a trusted remote
service or keeping enforcement-critical code off the customer's machine, no
local-only design can guarantee resistance to a determined source-code editor.
Do not reuse `Mridul.xxx` as a real-world account password; change the code hash
in `security_guard.py` before distributing this build if you want a different
shared code. Keep the source and release archives private.
