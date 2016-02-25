    use Encode::Arabic::ArabTeX;        # imports just like 'use Encode' would, plus extended options

    while ($line = <>) {                # maps the ArabTeX notation for Arabic into the Arabic script

        print encode 'utf8', decode 'arabtex', $line;       # 'ArabTeX' alias 'Lagally' alias 'TeX'
    }
