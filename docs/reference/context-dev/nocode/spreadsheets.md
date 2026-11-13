# Spreadsheets

> Display company logos in Google Sheets and Microsoft Excel with Logo Link.

Put a company domain such as `stripe.com` in cell `A2`. Copy your `brandLL_` public client ID from the [Logo Link dashboard](https://context.dev/dashboard/logolink), then use the formula for your spreadsheet.

> [tab] Google Sheets
>
> ```text theme={null}
> =IMAGE("https://logos.context.dev/?publicClientId=brandLL_xxx&domain=" & ENCODEURL(LOWER(TRIM(A2))))
> ```
>
> Fill down to display a logo for each domain. The default sizing mode fits the image while preserving its proportions; adjust the row height and column width. Mode `4` accepts custom height and width. See [Google's IMAGE reference](https://support.google.com/docs/answer/3093333).
>
> ![Logo Link in Google Sheets](https://mintcdn.com/branddev/U6_YUbxBeaDzLIAE/images/logolink-google-sheets.png?fit=max\&auto=format\&n=U6_YUbxBeaDzLIAE\&q=85\&s=8069a754608d9ad6a382396bba0c7f57)

> [tab] Microsoft Excel
>
> Use a version of Excel that supports `IMAGE`, such as Microsoft 365 or Excel 2024:
>
> ```text theme={null}
> =IMAGE("https://logos.context.dev/?publicClientId=brandLL_xxx&domain=" & LOWER(TRIM(A2)), A2 & " logo")
> ```
>
> The second argument provides alternative text. Sizing defaults to `0`, which fits the image while preserving its proportions; mode `3` accepts custom height and width. See [Microsoft's IMAGE reference](https://support.microsoft.com/en-us/excel/functions/image-function).
>
> ![Logo Link in Microsoft Excel](https://mintcdn.com/branddev/U6_YUbxBeaDzLIAE/images/logolink-microsoft-excel.png?fit=max\&auto=format\&n=U6_YUbxBeaDzLIAE\&q=85\&s=3b1068b6478a37da6687e5be12bcc4a0)

## Handle missing images

Keep the domain or company name visible even when the image cannot load. Wrap the formula in `IFERROR(your_formula, "")` if a blank cell is preferable to a formula error.

Logo Link can return an SVG fallback with HTTP 200. Google Sheets does not support SVG in `IMAGE`; Excel's supported formats and redirect rules can also prevent a browser-visible image from rendering. Check the response's media type when diagnosing a blank cell.

Google or Microsoft may fetch the image on their own infrastructure. Test the workbook with your configured [Domain Restrictions](https://docs.context.dev/brand/logo-link.md#before-you-start) before sharing it.

Use Logo Link as a direct image URL and follow its [usage restrictions](https://docs.context.dev/brand/logo-link.md#usage-restrictions). For company fields beyond logos, use [Zapier](https://docs.context.dev/nocode/zapier.md) or [Make](https://docs.context.dev/nocode/make.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.