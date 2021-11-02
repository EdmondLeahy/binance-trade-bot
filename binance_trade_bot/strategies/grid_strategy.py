import random
import sys
from datetime import datetime
import numpy as np

from binance_trade_bot.auto_trader import AutoTrader


class Strategy(AutoTrader):
    def initialize(self):
        super().initialize()
        self.initialize_current_coin()
        self.buy_grid_ratio = None
        self.sell_grid_ratio = None
        self.last_buy_ratio = None
        self.grid_size = 0.0005
        self.current_coin = self.db.get_current_coin()
        self.set_buy_sell_grid_lines()

    def set_buy_sell_grid_lines(self, last_buy_price=None):
        if not last_buy_price:
            curr_price = self.get_current_price_ratio(self.db.get_current_coin(), self.config.BRIDGE)
            self.logger.warning(f'No saved last buy price. Creating first at: {curr_price}')
            last_buy_price = curr_price

        self.buy_grid_ratio = np.round(last_buy_price*(1-self.grid_size), 2)
        self.sell_grid_ratio = np.round(last_buy_price*(1+self.grid_size), 2)
        self.logger.info(f'reset grid lines: {self.buy_grid_ratio } | {self.sell_grid_ratio}')
        self.last_buy_ratio = last_buy_price

    def get_current_price_ratio(self, coin1, coin2):
        return self.manager.get_ticker_price(coin1 + coin2)

    def scout(self):
        """
        Scout for potential buy or sell
        """
        # Display on the console, the current coin+Bridge, so users can see *some* activity and not think the bot has
        # stopped. Not logging though to reduce log size.
        self.logger.debug(f'Checking price of {self.current_coin + self.config.BRIDGE} \n')

        current_coin_price = self.get_current_price_ratio(self.current_coin, self.config.BRIDGE)

        if current_coin_price is None:
            self.logger.info("Skipping scouting... current coin {} not found".format(self.current_coin + self.config.BRIDGE))
            return
        self.logger.debug(f'current price: {current_coin_price}\n')
        self.determine_if_tradable(current_coin_price)

    def determine_if_tradable(self, current_price):
        if current_price < self.sell_grid_ratio:
            if current_price < self.buy_grid_ratio:
                self.buy_from_grid_trigger()
            else:
                self.logger.info(f'No action. Within the doldrums. {np.round(self.buy_grid_ratio - current_price,2)} | '
                                 f'{current_price} | '
                                 f'{np.round(self.sell_grid_ratio - current_price, 2)}')
                return

        else:
            self.sell_from_grid_trigger()
        self.set_buy_sell_grid_lines(last_buy_price=current_price)

    def buy_from_grid_trigger(self):
        # self.manager.buy_alt(self.current_coin, self.config.BRIDGE)
        self.logger.warning('STUBBED BUY CALL')

    def sell_from_grid_trigger(self):
        # self.manager.sell_alt(self.current_coin, self.config.BRIDGE)
        self.logger.warning('STUBBED SELL CALL')

    def bridge_scout(self):
        current_coin = self.db.get_current_coin()
        if self.manager.get_currency_balance(current_coin.symbol) > self.manager.get_min_notional(
            current_coin.symbol, self.config.BRIDGE.symbol
        ):
            # Only scout if we don't have enough of the current coin
            return
        new_coin = super().bridge_scout()
        if new_coin is not None:
            self.db.set_current_coin(new_coin)

    def initialize_current_coin(self):
        """
        Decide what is the current coin, and set it up in the DB.
        """
        if self.db.get_current_coin() is None:
            current_coin_symbol = self.config.CURRENT_COIN_SYMBOL
            if not current_coin_symbol:
                current_coin_symbol = random.choice(self.config.SUPPORTED_COIN_LIST)

            self.logger.info(f"Setting initial coin to {current_coin_symbol}")

            if current_coin_symbol not in self.config.SUPPORTED_COIN_LIST:
                sys.exit("***\nERROR!\nSince there is no backup file, a proper coin name must be provided at init\n***")
            self.db.set_current_coin(current_coin_symbol)

            # if we don't have a configuration, we selected a coin at random... Buy it so we can start trading.
            if self.config.CURRENT_COIN_SYMBOL == "":
                current_coin = self.db.get_current_coin()
                self.logger.info(f"Purchasing {current_coin} to begin trading")
                self.manager.buy_alt(current_coin, self.config.BRIDGE)
                self.logger.info("Ready to start trading")
