# crress-book


This is repo that compiles the book for the [CRRESS](https://labordynamicsinstitute.github.io/crress/) webinar series.

**Please check back** as more content is added after each webinar!

The book is compiled using [`pandoc`](https://pandoc.org/) for converting files to markdown, and [`quarto`](https://quarto.org/) for compiling the book.

This website is generated using Github Actions and uses a [workflow file](https://github.com/amichuda/quarto-crress-book/blob/e089ee92163c4e3f66bf9412965fcc1c0fb3cc7e/.github/workflows/publish.yml) for generating the book. THe workflow can be broken down into 3 main parts:

1. Setting up the environment
2. Installing python dependencies, pandoc and TeX (needed for using `quarto`)
3. A conversion script that takes various types of document files (but most likely Word files) and converts it to markdown with `pandoc`
4. A quarto action that compiles the website based on the `_config.yml` file.


Website can be found [here](https://amichuda.github.io/crress-book/)
