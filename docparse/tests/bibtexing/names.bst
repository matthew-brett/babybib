ENTRY
  { address
    author
    booktitle
    chapter
    edition
    editor
    howpublished
    institution
    journal
    key
    month
    note
    number
    organization
    pages
    publisher
    school
    series
    title
    type
    volume
    year
  }
  {}
  { label }

INTEGERS { nameptr namesleft numnames }

STRINGS { s t }

FUNCTION {format.names}
{ 's :=
 "--------------------------------" write$ newline$ 
 "string : " s * write$ newline$
  #1 'nameptr :=
  s num.names$ 'numnames :=

  numnames 'namesleft :=
  { namesleft #0 > }
    {
      numnames #1 >
        { "- author " nameptr int.to.str$ *
          "/" *
          numnames int.to.str$ *
          write$ newline$ }
        { skip$ }
      if$
    
      s nameptr "  First:{ ff}" format.name$ write$ newline$
      s nameptr "  von  :{ vv}" format.name$ write$ newline$
      s nameptr "  Last :{ ll}" format.name$ write$ newline$
      s nameptr "  jr   :{ jj}" format.name$ write$ newline$
      namesleft #1 - 'namesleft :=
      nameptr #1 + 'nameptr :=
    }
  while$
}
FUNCTION {format.authors}
{ author empty$
    { "" }
    { author format.names }
  if$
}

FUNCTION {book} {}
FUNCTION {article} {}
FUNCTION {booklet} {}
FUNCTION {inbook} {}
FUNCTION {incollection} {}
FUNCTION {inproceedings} {}
FUNCTION {manual} {}
FUNCTION {mastersthesis} {}
FUNCTION {misc} {}
FUNCTION {phdthesis} {}
FUNCTION {proceedings} {}
FUNCTION {techreport} {}
FUNCTION {unpublished} {}

FUNCTION { start.verbatim }
{
  preamble$ write$ newline$
  "\begin{verbatim}" write$ newline$
}
FUNCTION { end.verbatim }
{
  "\end{verbatim}" write$ newline$
}

READ

EXECUTE { start.verbatim }
ITERATE {format.authors}
EXECUTE { end.verbatim }

