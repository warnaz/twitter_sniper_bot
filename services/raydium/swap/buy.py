import asyncio
import datetime
import random
import time

from solders.pubkey import Pubkey
from solders.compute_budget import set_compute_unit_price,set_compute_unit_limit
from solana.rpc.types import TokenAccountOpts
from solana.rpc.commitment import Commitment, Confirmed, Finalized
from solana.rpc.api import RPCException
from solana.rpc.api import Client, Keypair
from solana.rpc.async_api import AsyncClient
from spl.token.client import Token
from spl.token.core import _TokenCore
from spl.token.instructions import (
    create_associated_token_account, 
    get_associated_token_address, 
    close_account, 
    CloseAccountParams
)

from loguru import logger
from dotenv import dotenv_values

from services.raydium.utils.create_close_account import fetch_pool_keys, make_swap_instruction
from ..config import GAS_LIMIT, GAS_PRICE, MAX_RETRIES, LAMPORTS_PER_SOL, RETRY_DELAY


async_solana_client = AsyncClient('https://api.mainnet-beta.solana.com')
solana_client = Client('https://api.mainnet-beta.solana.com')


# You can use getTimeStamp With Print Statments to evaluate How fast your transactions are confirmed
def getTimestamp():
    while True:
        timeStampData = datetime.datetime.now()
        currentTimeStamp = "[" + timeStampData.strftime("%H:%M:%S.%f")[:-3] + "]"
        return currentTimeStamp


async def get_token_account(ctx,
                                owner: Pubkey.from_string,
                                mint: Pubkey.from_string):
        try:
            account_data = await ctx.get_token_accounts_by_owner(owner, TokenAccountOpts(mint))
            return account_data.value[0].pubkey, None
        except:
            swap_associated_token_address = get_associated_token_address(owner, mint)
            swap_token_account_Instructions = create_associated_token_account(owner, owner, mint)
            return swap_associated_token_address, swap_token_account_Instructions


async def sell_and_buy(solana_client: Client, token_address, payer, amount, sell=None):
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            logger.info("Start try")
            # token_symbol, SOl_Symbol = getSymbol(token_address)
            mint = Pubkey.from_string(token_address)
            logger.info("Fetch pool keys")
            pool_keys = fetch_pool_keys(str(mint))
            amount_in = int(amount * LAMPORTS_PER_SOL)
            logger.info(f"Amount in: {amount_in}")
            accountProgramId = solana_client.get_account_info_json_parsed(mint)
            logger.info(accountProgramId)
            TOKEN_PROGRAM_ID = accountProgramId.value.owner

            balance_needed = Token.get_min_balance_rent_for_exempt_for_account(solana_client)
            swap_associated_token_address, swap_token_account_Instructions = await get_token_account(async_solana_client,payer.pubkey(),mint)
            WSOL_token_account, swap_tx, payer, Wsol_account_keyPair, opts, = _TokenCore._create_wrapped_native_account_args(
                TOKEN_PROGRAM_ID, payer.pubkey(), payer, amount_in,
                False, balance_needed, Commitment("confirmed")
            )

            if sell:
                token_to_buy = WSOL_token_account
                token_to_sell = swap_associated_token_address
            else:
                token_to_buy = swap_associated_token_address
                token_to_sell = WSOL_token_account

            instructions_swap = make_swap_instruction(amount_in,
                                                      token_to_buy, 
                                                      token_to_sell,
                                                      pool_keys,
                                                      mint,
                                                      solana_client,
                                                      payer)
            params = CloseAccountParams(account=WSOL_token_account, dest=payer.pubkey(), owner=payer.pubkey(),
                                        program_id=TOKEN_PROGRAM_ID)
            closeAcc = (close_account(params))
            if swap_token_account_Instructions != None:
                swap_tx.add(swap_token_account_Instructions)

            # Compute unit price and comute unit limit gauge your gas fees more explanations on how to calculate in a future article           
            unit_price_ix = set_compute_unit_price(GAS_PRICE)
            unit_limit_ix = set_compute_unit_limit(GAS_LIMIT)

            swap_tx.add(instructions_swap, unit_price_ix, unit_limit_ix, closeAcc)
            txn = solana_client.send_transaction(swap_tx, payer,Wsol_account_keyPair)
            txid_string_sig = txn.value
            if txid_string_sig:
                print("Transaction sent")
                # print(f"Transaction Signature Waiting to be confirmed: https://solscan.io/tx/{txid_string_sig}")
                print("Waiting Confirmation")

            await asyncio.sleep(2.5)
            logger.info("Confirm_transaction")
            logger.info(txid_string_sig)

            confirmation_resp = solana_client.confirm_transaction(
                txid_string_sig,
                commitment=Confirmed,
                sleep_seconds=1,
            )

            logger.info(confirmation_resp)

            if confirmation_resp.value[0].err == None and str(
                    confirmation_resp.value[0].confirmation_status) == "TransactionConfirmationStatus.Confirmed":
                print("Transaction Confirmed")
                print(f"Transaction Signature: https://solscan.io/tx/{txid_string_sig}")

                return

            else:
                print("Transaction not confirmed")
                return False
        except asyncio.TimeoutError:
            print("Transaction confirmation timed out. Retrying...")
            retry_count += 1
            time.sleep(RETRY_DELAY)
        except RPCException as e:
            print(f"RPC Error: [{e.args[0]}]... Retrying...")
            retry_count += 1
            time.sleep(RETRY_DELAY)
        except Exception as e:
            if "block height exceeded" in str(e):
                print("Transaction has expired due to block height exceeded. Retrying...")
                retry_count += 1
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise e
                print(f"Unhandled exception: {e}. Retrying...")
                retry_count += 1
                await asyncio.sleep(RETRY_DELAY)
        # except Exception as e:
        #     print(f"Unhandled exception: {e}. Retrying...")
        #     retry_count = MAX_RETRIES
        #     return False

    print("Failed to confirm transaction after maximum retries.")
    return False


async def buy_token(token_address: str, amount_in: float, private_key: str, sell: bool = False):
    logger.info("Run")
    logger.critical(f"Buying token: {token_address} with amount: {amount_in}")

    payer = Keypair.from_base58_string(private_key)

    buy_transaction = await sell_and_buy(
        solana_client=solana_client, 
        token_address=token_address, 
        payer=payer, 
        amount=amount_in,
        sell=sell
    )

    logger.info(buy_transaction)
