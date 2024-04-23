class Formatting:
    @staticmethod
    def format_monetary(value):
        return (
            f"R$ {value:,.2f}"
            .replace(",", "x")
            .replace(".", ",")
            .replace("x", ".")
        )