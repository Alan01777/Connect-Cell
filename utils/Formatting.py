class Formatting:
    @staticmethod
    def format_monetary(value):
        return (
            f"R$ {value:,.2f}"
            .replace(",", "x")
            .replace(".", ",")
            .replace("x", ".")
        )
    @staticmethod
    # formati all columns in the dataframe
    def format_dataframe(df):
        monetary_columns = [
            "(R$)PEÇA",
            "LUCRO BRUTO",
            "VALOR TOTAL DO SERVIÇO",
            "LUCRO LIQUIDO",
            "VALOR DO TÉCNICO",
        ]
        df["% DO TÉCNICO"] = (df["% DO TÉCNICO"] * 100).map("{:.0f}%".format)
        for column in monetary_columns:
            df[column] = df[column].map(Formatting.format_monetary)
        return df