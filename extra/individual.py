import yfinance as yf
import xlsxwriter


def individualReport():
    attrList = []
    prompt = "Enter the stock name (e.g. \"AAPL\"):\n"
    ticker = input(prompt)
    tick = yf.Ticker(ticker)

    attrList.append("Name")
    attrList.append("Value")
    attrList.append("Description")

    if "longBusinessSummary" in tick.info:
        attrList.append("Summary")
        attrList.append(tick.info["longBusinessSummary"])
        attrList.append("Summary of business")

    if "fullTimeEmployees" in tick.info:
        attrList.append("Employees")
        attrList.append(tick.info["fullTimeEmployees"])
        attrList.append("Number of employees")

    attrList.append("Target low price")
    attrList.append(tick.info["targetLowPrice"])
    attrList.append("Lowest price prediction")

    attrList.append("Target High Price")
    attrList.append(tick.info["targetHighPrice"])
    attrList.append("High price prediction")

    attrList.append("Target Mean Price")
    attrList.append(tick.info["targetMeanPrice"])
    attrList.append("Average price prediction")

    attrList.append("Target Median Price")
    attrList.append(tick.info["targetMedianPrice"])
    attrList.append("Less influenced by outliers")

    attrList.append("PEG Ratio")
    attrList.append(tick.info["pegRatio"]
                    )
    attrList.append(
        "Price-to-earnings growth, estimate of future earnings (positive is better)")

    attrList.append("Forward PE")
    attrList.append(tick.info["pegRatio"]
                    )
    attrList.append(
        "Forecasted price to earnings ratio, may be incorrect/biased")

    attrList.append("Book Value")
    attrList.append(tick.info["bookValue"])
    attrList.append("Amount everyone gets if company liquidates")

    attrList.append("Market Cap")
    attrList.append(tick.info["marketCap"])
    attrList.append("Price * Number of Shares")

    attrList.append("EBITDA Margin")
    attrList.append(tick.info["ebitdaMargins"])
    attrList.append(
        "More positive is better: company is profitable without factoring in Interests/Taxes/Depreciation/Amortization")

    attrList.append("Profit Margin")
    attrList.append(tick.info["profitMargins"]
                    )
    attrList.append("")

    attrList.append("Forward EPS")
    attrList.append(tick.info["profitMargins"]
                    )
    attrList.append(
        "Negative means company currently projected to lose money (short term), earnings per share")

    attrList.append("Price to Book")
    attrList.append(tick.info["priceToBook"]
                    )
    attrList.append(
        "Stock price versus Book value. Values under 1 are ideal, nothing over 3 should be considered")

    wb = xlsxwriter.Workbook("Report.xlsx")
    sheet = wb.add_worksheet()
    row = 0
    col = 0

    for item in attrList:
        sheet.write(row, col, item)
        col += 1
        if(col == 3):
            row += 1
            col = 0

    wb.close()
