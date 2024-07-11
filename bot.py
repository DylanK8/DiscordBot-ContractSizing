import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
import os

def calculate_contract_size(entry_price, stop_loss_price, risk_amount, point_value):
    points_risked = entry_price - stop_loss_price
    risk_dollars = points_risked * point_value
    contracts = risk_amount / risk_dollars
    return contracts

def calculate_risk_contracts(entry_price, stop_loss_price, point_value, num_contracts):
    points_risked = entry_price - stop_loss_price
    risk_dollars = points_risked * point_value
    total_risk = risk_dollars * num_contracts
    return total_risk, num_contracts
point_value = {"NQM": 20, "ESM": 50}

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)

@slash.slash(name="calculate_risk",
             description="Calculate contract size and risk",
             options=[
                 create_option(
                     name="instrument",
                     description="The trading instrument (NQ Mini or ES Mini)",
                     option_type=3,
                     required=True,
                     choices=[
                         {"name": "NQ Mini", "value": "NQM"},
                         {"name": "ES Mini", "value": "ESM"}
                     ]
                 ),
                 create_option(
                     name="entry_price",
                     description="The entry price",
                     option_type=10,
                     required=True
                 ),
                 create_option(
                     name="stop_loss_price",
                     description="The stop loss price",
                     option_type=10,
                     required=True
                 ),
                 create_option(
                     name="risk_amount",
                     description="The amount you want to risk",
                     option_type=10,
                     required=True
                 )
             ])
async def calculate_risk(ctx, instrument: str, entry_price: float, stop_loss_price: float, risk_amount: float):
    if ctx.channel.id != 1250486001323999263:
        await ctx.send("This command can only be used in <#1250486001323999263>")
        return

    point_value_instrument = point_value.get(instrument.upper())
    if point_value_instrument is None:
        await ctx.send("Invalid instrument. Please choose NQ Mini or ES Mini.")
        return

    contracts = calculate_contract_size(entry_price, stop_loss_price, risk_amount, point_value_instrument)
    message = f'Number of contracts needed: {contracts:.0f}\n'
    message += f'Entry price: {entry_price}, Stop loss price: {stop_loss_price}, Risk amount: {risk_amount}\n\n'

    num_contracts = int(contracts)
    lower_bound = max(num_contracts - 5, 1)  
    upper_bound = num_contracts + 5  
    for contract in range(upper_bound, lower_bound - 1, -1):
        risk, contracts = calculate_risk_contracts(entry_price, stop_loss_price, point_value_instrument, contract)
        message += f'{contracts:.0f} contracts | risk = ${risk:.0f}\n'

    await ctx.send(message)
token = os.getenv('DISCORD_TOKEN')

if token is None:
    print("DISCORD_TOKEN environment variable is not set.")
    exit(1)

bot.run(token)
