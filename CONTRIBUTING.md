### Translating

`find pozo/ -iname "*.py" | xargs xgettext --from-code utf-8 -o messages.pot --key`

This file goes in locale, then use poedit to edit translations.
