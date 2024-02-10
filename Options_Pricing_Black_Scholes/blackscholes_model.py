'''
@project       : Temple University CIS 4360 Computational Methods in Finance
@Instructor    : Dr. Alex Pang

@Student Name  : Giorgio Tatarelli

@Date          : 11/2023

Black-Schole Model

'''

import datetime
from scipy.stats import norm
from math import log, exp, sqrt
import os

from stock import Stock
import option
import sqlite3
from financial_option import *

class BlackScholesModel(object):
    '''
    Implementation of the Black-Schole Model for pricing European options
    '''

    def __init__(self, pricing_date, risk_free_rate):
        self.pricing_date = pricing_date
        self.risk_free_rate = risk_free_rate

    def calc_parity_price(self, option, option_price):
        '''
        return the put price from Put-Call Parity if input option is a call
        else return the call price from Put-Call Parity if input option is a put
        '''
        result = None

        if option.option_type == FinancialOption.Type.CALL:
            result = option_price + option.strike * exp(-self.risk_free_rate * option.time_to_expiry) - option.underlying.spot_price
        elif option.option_type == FinancialOption.Type.PUT:
            result = option_price - option.strike * exp(-self.risk_free_rate * option.time_to_expiry) + option.underlying.spot_price
       
        return(result)

    def calc_model_price(self, option):
        '''
        Calculate the price of the option using Black-Scholes model
        '''
        px = None
        if option.option_style == FinancialOption.Style.AMERICAN:
            raise Exception("B\S price for American option not implemented yet")
        else:
            S0 = option.underlying.spot_price
            sigma = option.underlying.sigma
            T = option.time_to_expiry
            K = option.strike
            q = option.underlying.dividend_yield
            r = self.risk_free_rate

            d1 = (log(S0/K)+(r-q+pow(sigma, 2)/2)*T)/(sigma * sqrt(T))
            d2 = d1 - (sigma * sqrt(T))

            if(option.option_type == FinancialOption.Type.CALL):
                px = S0* norm.cdf(d1) - K*exp(-r*T)*norm.cdf(d2)
            else:
                px = K * exp(-r*T)*norm.cdf(-d2) - S0*norm.cdf(-d1)

        return(px)

    def calc_delta(self, option):
        if option.option_style == FinancialOption.Style.AMERICAN:
            raise Exception("B\S price for American option not implemented yet")
        elif option.option_style == FinancialOption.Style.EUROPEAN:
            S0 = option.underlying.spot_price
            K = option.strike
            T = option.time_to_expiry
            r = self.risk_free_rate
            q = option.underlying.dividend_yield
            sigma = option.underlying.sigma
            
            d1 = (log(S0/K)+(r-q+pow(sigma, 2)/2)*T)/(sigma * sqrt(T))

            if(option.option_type == FinancialOption.Type.CALL):
                result = norm.cdf(d1)
            else:
                result = norm.cdf(d1) - 1
        else:
            raise Exception("Unsupported option type")

        return result

    def calc_gamma(self, option):

        if option.option_style == FinancialOption.Style.AMERICAN:
            raise Exception("B\S price for American option not implemented yet")
        elif option.option_style == FinancialOption.Style.EUROPEAN:
            S0 = option.underlying.spot_price
            K = option.strike
            T = option.time_to_expiry
            r = self.risk_free_rate
            q = option.underlying.dividend_yield
            sigma = option.underlying.sigma
            
            d1 = (log(S0/K)+(r-q+pow(sigma, 2)/2)*T)/(sigma * sqrt(T))
            
            result = (norm.pdf(d1)*exp(-q*T))/(S0*sigma*sqrt(T))
        else:
            raise Exception("Unsupported option type")

        return result

    def calc_theta(self, option):
        if option.option_style == FinancialOption.Style.AMERICAN:
            raise Exception("B\S price for American option not implemented yet")
        elif option.option_style == FinancialOption.Style.EUROPEAN:
            S_0 = option.underlying.spot_price
            K = option.strike
            T = option.time_to_expiry
            r = self.risk_free_rate
            q = option.underlying.dividend_yield
            sigma = option.underlying.sigma
            d1 = (np.log(S_0 / K) + (r - q + sigma ** 2 / 2) * T) / (sigma * sqrt(T))
            d2 = d1 - sigma * sqrt(T)

            if option.option_type == FinancialOption.Type.CALL:
                result = (-S_0 * norm.pdf(d1) * sigma * exp(-q * T)) / (2 * sqrt(T)) + \
                         (q * S_0 * norm.cdf(d1) * exp(-q * T)) - (r * K * exp(-r * T) * norm.cdf(d2))
            else:
                result = (norm.pdf(d1) * exp(-q * T)) / (S_0 * sigma * sqrt(T)) - \
                         (q * S_0 * norm.cdf(-d1) * exp(-q * T)) + (r * K * exp(-r * T) * norm.cdf(-d2))
        else:
            raise Exception("Unsupported option type")

        return result

    def calc_vega(self, option):
        if option.option_style == FinancialOption.Style.AMERICAN:
            raise Exception("B\S price for American option not implemented yet")
        elif option.option_style == FinancialOption.Style.EUROPEAN:
            S0 = option.underlying.spot_price
            K = option.strike
            T = option.time_to_expiry
            r = self.risk_free_rate
            q = option.underlying.dividend_yield
            sigma = option.underlying.sigma
            d1 = (np.log(S0 / K) + (r - q + sigma ** 2 / 2) * T) / (sigma * sqrt(T))

            result = S0 * sqrt(T) * norm.pdf(d1) * exp(-q*T)
        else:
            raise Exception("Unsupported option type")

        return result

    def calc_rho(self, option):
        if option.option_style == FinancialOption.Style.AMERICAN:
            raise Exception("B\S price for American option not implemented yet")
        elif option.option_style == FinancialOption.Style.EUROPEAN:
            S_0 = option.underlying.spot_price
            K = option.strike
            T = option.time_to_expiry
            r = self.risk_free_rate
            sigma = option.underlying.sigma
            q = option.underlying.dividend_yield
            d1 = (np.log(S_0 / K) + (r - q + sigma ** 2 / 2) * T) / (sigma * sqrt(T))
            d2 = d1 - sigma * sqrt(T)

            if(option.option_type == FinancialOption.Type.CALL):
                result = K * T * exp(-r*T) * norm.cdf(d2)
            else:
                result = -K * T * exp(-r*T) * norm.cdf(-d2)
        else:
            raise Exception("Unsupported option type")
        return result


def _test():
    # put in any unit tests you want
    parser = option.get_default_parser()
    parser.add_argument('--data_dir', dest = 'data_dir', default='./data', help='data dir')    
    
    args = parser.parse_args()
    opt = option.Option(args = args)

    opt.output_dir = os.path.join(opt.data_dir, "daily")
    opt.sqlite_db = os.path.join(opt.data_dir, "sqlitedb/Equity.db")

    db_file = opt.sqlite_db
    db_connection = sqlite3.connect(db_file)

    print(vars(opt))
    
    symbol = 'AAPL'
    freq = 'annual'
    stock = Stock(opt, db_connection, symbol, spot_price = 42, sigma = 0.2, freq = freq)

    bs = BlackScholesModel(pricing_date = "today", risk_free_rate = 0.1)
    call_opt = EuropeanCallOption(stock, 0.5, 40)

    print("Call Option")
    print("Price: ", bs.calc_model_price(call_opt))
    print("Delta: ", bs.calc_delta(call_opt))
    print("Gamma: ", bs.calc_gamma(call_opt))
    print("Theta: ", bs.calc_theta(call_opt))
    print("Vega: ", bs.calc_vega(call_opt))
    print("Rho: ", bs.calc_rho(call_opt))

    put_opt = EuropeanPutOption(stock, 0.5, 40)

    print("Put Option")
    print("Price: ", bs.calc_model_price(put_opt))
    print("Delta: ", bs.calc_delta(put_opt))
    print("Gamma: ", bs.calc_gamma(put_opt))
    print("Theta: ", bs.calc_theta(put_opt))
    print("Vega: ", bs.calc_vega(put_opt))
    print("Rho: ", bs.calc_rho(put_opt))

if __name__ == "__main__":
    _test()
