# solid-rock-hb

![Solid Rock Hebrew Bible, edited by Stephen L. Brown](https://github.com/jjmccollum/solid-rock-hb/blob/master/tex/img/srhb-social-preview.png)

[![CC BY 4.0][cc-by-shield]][cc-by]

## About the Book

From the back cover:

> While scribes have transmitted the Hebrew Bible in its original languages with extraordinary care for millennia, no one copyist can be expected to have escaped all error. The surviving tradition has accumulated many points of variation over time, and some of these pose unavoidable challenges for translation and exegesis. In many other ancient works, new editions based on a critical assessment of variant readings have offered valuable insights to interpreters, but readers of the Hebrew Bible have so far not had this benefit.

> The _Solid Rock Hebrew Bible_ aims to remedy this situation. Based on investigation of various masoretic manuscripts, ancient manuscripts from the Judean wilderness, the ancient versions, and other sources, this edition prints the entire Hebrew text (in a traditional two-column layout and an easy-to-read 13-point font, with vowel points included for readers' convenience) and includes adjustments made to the base text (the Leningrad Codex) in over 2,500 places. Additionally, over 2,000 other adjustments have been made to the diacritics. Pastors, scholars, translators, and others readers of the Hebrew Bible will stand to benefit from this work.

The _Solid Rock Hebrew Bible_ is available in two printed volumes at Barnes & Noble ([Volume 1](https://www.barnesandnoble.com/w/solid-rock-hebrew-bible-volume-1-stephen-l-brown/1142861227), [Volume 2](https://www.barnesandnoble.com/w/solid-rock-hebrew-bible-volume-2-stephen-l-brown/1142861235)), Amazon ([Volume 1](https://www.amazon.com/dp/0999532227), [Volume 2](https://www.amazon.com/dp/0999532235)), and other booksellers.

## Features

The _Solid Rock Hebrew Bible_ includes several textual and paratextual features to facilitate reading and reference.
Section markers are typeset with notation intended to stand out among the text without being distracting: open sections breaks are marked with multiple line breaks containing an inverted _nun_, and closed section breaks are marked with small spaces in the start or middle of their line, respectively.
For ease of reference, chapter and verse numbers are set in the text, and running scripture indices occur in the top margin of every page.

The text of the _Solid Rock Hebrew Bible_ has been collated against version 1.6 of the [Unicode/XML Leningrad
Codex (UXLC)](http://www.tanach.us/).
Variants are noted with standard text-critical sigla for additions, omissions, substitutions, and transpositions familiar to readers of the Nestle-Aland critical text of the New Testament, the _SBL Greek New Testament_, and the _Solid Rock Greek New Testament_.
If multiple differences of the same type occur in the same verse, then their sigla in both the text and the bottom margin are differentiated by superscript numbers.
Where a variant concerns the placement of a verse break, the verse break will be printed in one or both readings in the bottom margin.

These features are illustrated in the sample of Ezekiel below:

![Features in the text and apparatus demonstrated in a sample page of Ezek 41–42](https://github.com/jjmccollum/solid-rock-hb/blob/master/tex/img/features.png)

Note the distinct sigla used for addition (42:1), omission (41:22), and substitution (everywhere else); the labels used to distinguish between different changes of the same type in the same verse (substitution in 41:22, addition in 42:12); and the inclusion of verse numbers in one or more readings where a textual difference affects their placement (in 41:21).

The Hebrew text includes vowel points, but no cantillation marks.
It is typeset in a slightly modified version of Yoram Gnat's Keter YG that features improved vowel placement, additional substitution rules (e.g., furtive _patach_), and classical and discretionary ligatures (e.g., correct handling of combined vowels at the end of _Yerushalaim_ and contextual merging of _holam_ with a following _shin_ dot or preceding _sin_ dot).
This typeface is maintained in a separate repo at https://github.com/jjmccollum/Keter-YG.

## About the Editor

**Stephen L. Brown** began studying biblical Hebrew in his early teen years, and later set about studying other languages (particularly biblical Aramaic and Greek) as well as textual criticism of a variety of works, particularly the Old and New Testaments. He served for five years as a pastor at First Baptist Church in North Conway, NH, and currently lives in Philadelphia, PA.

## About This Repository

This repository contains the digital infrastructure behind the _Solid Rock Hebrew Bible_.
For those interested in analyzing and augmenting the underlying collation between this edition and the Unicode/XML Leningrad
Codex, v1.6, the files of primary interest are the TEI XML transcription and collation files in the `xml` directory.
For those interested in some ancillary tools developed for converting, normalizing, and collating transcriptions and transforming TEI XML collations into ConTeXt files, these tools can be found in the `py` directory.
(Be warned that these scripts may seem unpolished, as they were designed for private use.)
Finally, for those interested in the typeset work, the ConTeXt files used to generate this can be found in the `tex` directory.
If you are looking for PDFs of both volumes of this work, you can find them at the top level of the repository in the `vol_1.pdf` and `vol_2.pdf` files.

## License and Citation

The TEI XML transcription and collation files, the Python scripts, and the TeX files used for maintaining and typesetting this work are licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg

Under this license, you are free to use and modify the material in this repository, as long as you cite the original work:

> Stephen L. Brown, ed. _Solid Rock Hebrew Bible_. 2 vols. North Conway, NH: Solid Rock Publications, 2022.

## Contact

All questions, corrections, and other feedback should be directed to contact-dot-solidrockpublications-at-gmail-dot-com.
