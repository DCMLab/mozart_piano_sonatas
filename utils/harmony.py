# Regular expression needs to be compiled using re.compile(regex, re.VERBOSE)
regex = r"""
    ^(\.?
        ((?P<globalkey>[a-gA-G](b*|\#*))\.)?
        ((?P<localkey>(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i))\.)?
        ((?P<pedal>(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i))\[)?
        (?P<chord>
            (?P<numeral>(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i|Ger|It|Fr|@none))
            (?P<form>(%|o|\+|M|\+M))?
            (?P<figbass>(7|65|43|42|2|64|6))?
            (\((?P<changes>((\+|-|\^)?(b*|\#*)\d)+)\))?
            (/(?P<relativeroot>((b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i)/?)*))?
        )
        (?P<pedalend>\])?
    )?
    (?P<phraseend>(\\\\|\{|\}|\}\{))?$
    """
