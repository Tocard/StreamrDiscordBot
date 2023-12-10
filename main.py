import discord
import logging
import json
from config import load_config
import humanize
from datetime import datetime

from harvest_operator import harvest_operator_info, harvest_all_operators_info
from utils import convert_json_type, get_slashed_amount, get_delegator_address, normalize

cfg = load_config()
MY_GUILD = discord.Object(cfg["guild"])
GWEI_CONST = cfg["GWEI_CONST"]

logging.basicConfig(level=logging.INFO)
discord_logger = logging.getLogger('discord')


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    for guild in client.guilds:
        print("{} is connected to the following guild:".format(client.user))
        print("{} ( id: {} )".format(guild.name, guild.id))


@client.tree.command(name="operators", description="get operator info")
@discord.app_commands.describe(operators_id='harvest this operator information')
async def operators(interaction: discord.Interaction, operators_id: str):
    embed = discord.Embed(
        color=discord.Color.purple(),
    )
    operator = convert_json_type(harvest_operator_info(operators_id))
    meta_string = json.loads(operator["metadataJsonString"])
    embed.add_field(name="Name", value="{}".format(meta_string["name"]), inline=False)
    embed.add_field(name="Owner", value="{}".format(operator["owner"]), inline=True)
    embed.add_field(name="redundancyFactor", value="{}".format(meta_string["redundancyFactor"]), inline=True)

    embed.add_field(name="Total Earning Collected", value="{}".format(humanize.intcomma(operator["_cumulativeProfitsWei"], 2)), inline=False)
    embed.add_field(name="Operator Cut", value="{}".format(humanize.intcomma(operator["_operatorsCutFraction"], 2)), inline=True)
    embed.add_field(name="Blance on Operator", value="{}".format(humanize.intcomma(operator["_dataTokenBalanceWei"], 2)), inline=True)
    embed.add_field(name="Total Staked", value="{}".format(humanize.intcomma(operator["_totalStakeInSponsorshipsWei"], 2)), inline=True)
    embed.add_field(name="valueWithoutEarnings", value="{}".format(humanize.intcomma(operator["_valueWithoutEarnings"], 2)), inline=True)

    embed.add_field(name="SlashEvent", value="{}".format(len(operator["slashingEvents"])), inline=False)
    embed.add_field(name="SlashAmount", value="{}".format(humanize.intcomma(get_slashed_amount(operator["slashingEvents"]), 2)), inline=True)
    await interaction.response.send_message(embed=embed,)


@client.tree.command(name="slash_history", description="display all slash history")
async def slash_history(interaction):

    operators = harvest_all_operators_info()
    slash_event = []
    for operator in operators["data"]["operators"]:
        if len(operator['slashingEvents']) > 0:
            meta_string = json.loads(operator["metadataJsonString"])
            slash_event.append({"id": operator["id"], "name": meta_string["name"], "SlashCount":  len(operator['slashingEvents']), "SlashAmountLost": get_slashed_amount(operator['slashingEvents'])})

    i = 0
    for event in slash_event:
        embed = discord.Embed(
            color=discord.Color.red(),
        )
        embed.add_field(name=event["name"],
                        value="{}".format(event["id"]), inline=False)
        embed.add_field(name="SlashCount",
                        value="{}".format(event["SlashCount"]), inline=False)
        embed.add_field(name="SlashAmountLost",
                        value="{}".format(humanize.intcomma(event["SlashAmountLost"]), 2), inline=False)
        if i == 0:
            i = 1
            await interaction.response.send_message(embed=embed,)
        else:
            await interaction.followup.send(embed=embed, )


@client.tree.command(name="operator_slash_info", description="display slash history for one validator")
async def operator_slash_info(interaction: discord.Interaction, operators_id: str, detailed_mode: bool = False):

    operator = convert_json_type(harvest_operator_info(operators_id))
    meta_string = json.loads(operator["metadataJsonString"])
    slash = {"id": operator["id"], "name": meta_string["name"], "SlashCount":  len(operator['slashingEvents']), "SlashAmountLost": get_slashed_amount(operator['slashingEvents'])}

    if len(operator['slashingEvents']) > 0:
        embed = discord.Embed(color=discord.Color.red(),)
    else:
        embed = discord.Embed(color=discord.Color.green(),)

    embed.add_field(name=slash["name"],
                    value="{}".format(slash["id"]), inline=False)
    embed.add_field(name="SlashCount",
                    value="{}".format(slash["SlashCount"]), inline=False)
    embed.add_field(name="SlashAmountLost",
                    value="{}".format(humanize.intcomma(slash["SlashAmountLost"]), 2), inline=False)

    await interaction.response.send_message(embed=embed,)

    if detailed_mode:
        for slash_event in operator['slashingEvents']:
            embed = discord.Embed(
                color=discord.Color.red(),
            )
            embed.add_field(name="SlashDate",
                            value="{}".format(datetime.utcfromtimestamp(int(slash_event["date"])).strftime('%Y-%m-%d %H:%M:%S')), inline=False)
            embed.add_field(name="SlashAmountLost",
                            value="{}".format(humanize.intcomma(float(slash_event["amount"]) * GWEI_CONST), 2), inline=False)
            await interaction.followup.send(embed=embed, )


@client.tree.command(name="network_info", description="grab and display data from network")
async def network_info(interaction):

    operators = harvest_all_operators_info()
    slash_count = 0
    slash_amount_lost = 0
    delegator_count = 0
    unique_delegator_count = []
    total_stake_in_sponsorships_wei = 0
    operator_count = len(operators["data"]["operators"])
    node_slashed = 0
    for operator in operators["data"]["operators"]:
        if len(operator['slashingEvents']) > 0:
            slash_count = slash_count + len(operator['slashingEvents'])
            slash_amount_lost = slash_amount_lost + get_slashed_amount(operator['slashingEvents'])
            node_slashed = node_slashed + 1
        delegator_count = delegator_count + operator["delegatorCount"]
        unique_delegator_count = get_delegator_address(operator['delegations']) + unique_delegator_count
        total_stake_in_sponsorships_wei = total_stake_in_sponsorships_wei + float(operator['totalStakeInSponsorshipsWei'])

    embed = discord.Embed(color=discord.Color.orange(),)
    unique_values = list(set(unique_delegator_count))

    embed.add_field(name="Slash Count",
                    value="{}".format(slash_count), inline=False)
    embed.add_field(name="Number of node Slashed",
                    value="{}".format(node_slashed), inline=False)
    embed.add_field(name="% of Node slashed at least once",
                    value="{}".format(normalize(node_slashed / operator_count * 100)), inline=False)
    embed.add_field(name="Slash Amount Lost ",
                    value="{}".format(normalize(slash_amount_lost * GWEI_CONST)), inline=False)
    embed.add_field(name="Total Stream Staked",
                    value="{}".format(normalize(total_stake_in_sponsorships_wei * GWEI_CONST)), inline=False)
    embed.add_field(name="% lost by Slash",
                    value="{}".format(normalize(slash_amount_lost / total_stake_in_sponsorships_wei * 100 * GWEI_CONST)), inline=False)
    embed.add_field(name="Number Of Delegation",
                    value="{}".format(delegator_count), inline=False)
    embed.add_field(name="Number Of Delegator",
                    value="{}".format(len(unique_values)), inline=False)
    embed.add_field(name="Number Of Operator",
                    value="{}".format(operator_count), inline=False)
    await interaction.response.send_message(embed=embed,)

client.run(cfg["token"])
