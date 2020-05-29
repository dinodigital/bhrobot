import re

buy_for_x = re.compile('^/buy\s[a-zA-Z]+\sfor\s(\d|\d.\d)+\s[a-zA-Z]+\sat\s(\d|\d.\d)+$')
buy_for_x_loss_profit = re.compile('^/buy\s[a-zA-Z]+\sfor\s(\d|\d.\d)+\s[a-zA-Z]+\sat\s(\d|\d.\d)+(\s[+|-](\d|\d.\d)+%*)*(\s[+|-](\d|\d.\d)+%*)*$')
buy_x_for = re.compile('^/buy\s(\d|\d.\d)+\s[a-zA-Z]+\sfor\s[a-zA-Z]+\sat\s(\d|\d.\d)+$')
buy_x_for_loss_profit = re.compile('^/buy\s(\d|\d.\d)+\s[a-zA-Z]+\sfor\s[a-zA-Z]+\sat\s(\d|\d.\d)+(\s[+|-](\d|\d.\d)+%*)*(\s[+|-](\d|\d.\d)+%*)*$')
mbuy_for_x = re.compile('^/buy\s[a-zA-Z]+\sfor\s(\d|\d.\d)+\s[a-zA-Z]+$')
mbuy_x_for = re.compile('^/buy\s(\d|\d.\d)+\s[a-zA-Z]+\sfor\s[a-zA-Z]+$')


def is_buy_for_x(text):
    match = re.match(r'^/buy\s[a-zA-Z]+\sfor\s(\d|\d.\d)+\s[a-zA-Z]+\sat\s(\d|\d.\d)+', text)
    return True if match is not None else False


def is_buy_x_for(text):
    match = re.match(r'^/buy\s(\d|\d.\d)+\s[a-zA-Z]+\sfor\s[a-zA-Z]+\sat\s(\d|\d.\d)+', text)
    return True if match is not None else False
