from pandas.io.formats.style import Styler

TEXT_ALIGN_LEFT = {"props": [("text-align", "left")]}
TEXT_ALIGN_RIGHT = {"props": [("text-align", "right")]}
DISPLAY_NONE = {"props": [("display", "none")]}


def merge_props(d1, d2):
    return {"props": [*d1["props"], *d2["props"]]}


def object_and_date_type_columns(df):
    """Return the list of columns which are of object or datetime type
    
    Parameters
    ----------
    df: pandas.DataFrame
    
    Returns
    -------
    List[str]
    """
    return [
        column_name
        for column_name, column_type in df.dtypes.to_dict().items()
        if column_type in ["O", "<M8[ns]"]
    ]


class TableStyler(Styler):
    """
    Styler class with the following defaults:
    - headings are aligned left and uppercase;
    - text and datetime columns are aligned left;
    
    Attributes
    ----------
    background: str
        Color for the background headings and even rows
        
    foreground: str
        Color for the text of the headings
        
    Example
    -------
    >>> TableStyler(
            pandas.DataFrame(
                data={
                    "Text column": 3 * ["This is long enough"] + 3 * ["This is short"],
                    "Number column": 6 * [1],
                    "Date column quite long": pandas.date_range(
                        start="1970-01-01", periods=6, freq="d"
                    ),
                }
            )
        ).hide_index()
    
    """

    @staticmethod
    def get_text_column_styles(df):
        text_column_styles = []
        text_columns = df.pipe(object_and_date_type_columns)
        for n, column in enumerate(df.columns):
            text_align = TEXT_ALIGN_LEFT if column in text_columns else TEXT_ALIGN_RIGHT
            text_column_styles.append({"selector": "td.col{}".format(n), **text_align})
        return text_column_styles

    @staticmethod
    def get_default_styles(background, foreground):
        tabular_nums = {"props": [("font-variant-numeric", "tabular-nums")]}
        headings = {
            "props": [
                ("text-transform", "uppercase"),
                ("color", foreground),
                ("background", background),
                ("border-collapse", ""),
            ]
        }
        even_row_color = {"props": [("background", background)]}
        return [
            {"selector": "table", **tabular_nums},
            {"selector": "th.col_heading", **merge_props(TEXT_ALIGN_LEFT, headings)},
            {"selector": "tr:nth-child(even)", **even_row_color},
        ]

    def __init__(self, data, background="#fff4f9", foreground="#b28d9f"):
        styles = self.get_default_styles(
            background, foreground
        ) + self.get_text_column_styles(data)
        super().__init__(data, table_styles=styles)
