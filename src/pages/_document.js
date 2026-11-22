import Document, { Html, Head, Main, NextScript } from "next/document";

class MyDocument extends Document {
  render() {
    return (
      <Html lang="en" suppressHydrationWarning>
<Head>
           <script
             dangerouslySetInnerHTML={{
               __html: `(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme: dark)').matches)){document.documentElement.setAttribute('data-theme','dark');}}catch(e){}})();`,
             }}
           />
           <script async src="https://www.googletagmanager.com/gtm.js?id=GTM-PL2SZWCF" />
           <script
             dangerouslySetInnerHTML={{
               __html: `window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date());`,
             }}
           />
          <link rel="manifest" href={`${process.env.BASE_PATH || process.env.NEXT_PUBLIC_BASE_PATH || ""}/manifest.json`} />
          <meta name="theme-color" content="#3b5bdb" media="(prefers-color-scheme: light)" />
          <meta name="theme-color" content="#141210" media="(prefers-color-scheme: dark)" />
          <link rel="icon" href={`${process.env.BASE_PATH || process.env.NEXT_PUBLIC_BASE_PATH || ""}/icon.svg`} type="image/svg+xml" />
          <link rel="apple-touch-icon" href={`${process.env.BASE_PATH || process.env.NEXT_PUBLIC_BASE_PATH || ""}/icon.svg`} />
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default MyDocument;