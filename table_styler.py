from pandas.io.formats.style import Styler

TEXT_ALIGN_LEFT = {"props": [("text-align", "left")]}
TEXT_ALIGN_RIGHT = {"props": [("text-align", "right")]}
DISPLAY_NONE = {"props": [("display", "none")]}


def merge_props(d1, d2):
    return {"props": [*d1["props"], *d2["props"]]}


def select_columns_by_type(df, dtypes):
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
        if column_type in dtypes
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

    Methods
    -------
    format_columns(numerical_format=None, date_format=None)
        Format numerical and date-like columns based on numerical_format
        and date_format

        
    Example
    -------
    >>> df = pandas.DataFrame(
            data={
                "Text column": 3 * ["This is long enough"] + 3 * ["This is short"],
                "Number column": 3 * [91] + 3 * [1243],
                "Another Number column": 3 * [91] + 3 * [1243],
                "Date column quite long": pandas.date_range(
                    start="1970-01-01", periods=6, freq="d"
                ),
            }
        )

    >>> (
            TableStyler(df)
            .hide_index()
            .format_columns(numerical_format="{:,}", date_format="{:%b %d, %Y}")
            .render()
        )

    # To make the table scrollable, embed it in a div environment
    >>> s = "<div style='width: 100%; height: 100%; overflow: auto;'>{}</div>".format(
        TableStyler(df).hide_index().render()
    )
    
    """

    @staticmethod
    def get_text_column_styles(columns, text_columns):
        text_column_styles = []
        # text_columns = df.pipe(object_and_date_type_columns)
        for n, column in enumerate(columns):
            text_align = TEXT_ALIGN_LEFT if column in text_columns else TEXT_ALIGN_RIGHT
            text_column_styles.append({"selector": "td.col{}".format(n), **text_align})
        return text_column_styles

    @staticmethod
    def get_default_styles(background, foreground):
        table = {
            "props": [
                ("font-variant-numeric", "tabular-nums"),
                ("border-spacing", "0"),
                ("line-height", "2"),
            ]
        }
        headings = {
            "props": [
                ("text-transform", "uppercase"),
                ("color", foreground),
                ("background", background),
                ("border-collapse", ""),
            ]
        }
        even_row_color = {"props": [("background", background)]}
        cell_padding = {"props": [("padding", "0 1ch")]}
        return [
            # By passing an empty selector, the props are added at the ID level
            # allowing to style the table itself
            {"selector": "", **table},
            {"selector": "th.col_heading", **merge_props(TEXT_ALIGN_LEFT, headings)},
            {"selector": "tr:nth-child(even)", **even_row_color},
            {"selector": "th, tr, td", **cell_padding},
        ]

    def __init__(self, data, background="#fff4f9", foreground="#b28d9f"):
        super().__init__(data)

        # self.data is now defined
        styles = self.get_default_styles(
            background, foreground
        ) + self.get_text_column_styles(
            self.columns, self.object_columns + self.date_columns
        )
        # table_styles can not be declared in the parent __init__ because styles makes
        # use of self.data which is only defined after initializing the instance
        self.table_styles = styles

    @property
    def object_columns(self):
        return select_columns_by_type(self.data, dtypes=["O"])

    @property
    def date_columns(self):
        return select_columns_by_type(self.data, dtypes=["<M8[ns]"])

    @property
    def numerical_columns(self):
        return list(
            set(self.data.columns) - set(self.object_columns + self.date_columns)
        )

    def format_columns(self, numerical_format=None, date_format=None):
        """Format numerical and dates columns
        
        Parameters
        ----------
        numerical_format: str = None
            Format for numerical column, for example {:,}
        date_format: str = None
            Format for the date columns, for example {: %Y %m %d}"""

        styler = self
        if numerical_format:
            styler = styler.format(
                formatter=numerical_format, subset=self.numerical_columns
            )
        if date_format:
            styler = styler.format(formatter=date_format, subset=self.date_columns)
        return styler
