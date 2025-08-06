import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import gspread
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)

import os
import json
import gspread
from google.oauth2.service_account import Credentials

# Leer credenciales desde variable de entorno
credentials_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

# Scopes necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"],
["https://www.googleapis.com/auth/drive"]

# Crear credenciales
creds = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)

# Autenticación gspread
gc = gspread.authorize(creds)

sh = gc.open("Gastos Diarios")
worksheet = sh.sheet1

# Función para manejar mensajes
async def save_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        parts = text.split()

        if len(parts) < 3:
            raise ValueError("Faltan datos")

        categoria = parts[0]
        monto_str = parts[1].replace(",", ".")
        observaciones = " ".join(parts[2:])

        monto = float(monto_str)
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        worksheet.append_row([fecha, categoria, monto, observaciones])
        await update.message.reply_text(
            f"✅ Gasto registrado:\nCategoría: {categoria}\nMonto: ${monto:.2f}\nObservaciones: {observaciones}"
        )

    except ValueError:
        await update.message.reply_text("⚠️ Formato incorrecto. Usá: categoría monto observaciones\nEj: comida 1500 cena con amigos")
    except Exception as e:
        await update.message.reply_text("❌ Ocurrió un error al guardar el gasto.")
        print(f"Error al guardar gasto: {e}")


# Iniciar el bot
TOKEN = "7578655379:AAGtMfrOrLEHou3v-tKCfVZrIuker7JGzzs"
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_expense))

app.run_polling()



