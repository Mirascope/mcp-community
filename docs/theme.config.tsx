import type { DocsThemeConfig } from "nextra-theme-docs";
import { Logo } from "@/components/Logo";
import { SlackLogo } from "@/components/SlackLogo";
import Script from "next/script";

const config: DocsThemeConfig = {
  logo: <Logo width="48" height="48" />,
  color: {
    hue: 14,
    saturation: 75,
    lightness: {
      dark: 63,
      light: 63,
    },
  },
  head: (
    <>
      <title>MCP Community</title>
      <link
        rel="icon"
        type="image/svg+xml"
        sizes="any"
        href="/static/favicon.svg"
      />
      <meta
        name="description"
        content="Easily implement, deploy and use MCP servers"
      />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta property="og:title" content="MCP Community" />
      <meta
        property="og:description"
        content="Easily implement, deploy and use MCP servers"
      />
      <meta property="og:image" content="/static/og-image.png" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content="MCP Community" />
      <meta
        name="twitter:description"
        content="Easily implement, deploy and use MCP servers"
      />
      <meta name="twitter:image" content="/static/og-image.png" />
      <Script
        async
        src="https://www.googletagmanager.com/gtag/js?id=G-WGR8G7YGLH"
      ></Script>
      <Script>
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-WGR8G7YGLH');
        `}
      </Script>
    </>
  ),
  footer: {
    content: (
      <div className="max-w-7xl">
        <div className="flex justify-start items-center gap-2 mb-4">
          <Logo width="24" height="24" />
          <span className="font-medium">MCP Community</span>
        </div>
        <p className="text-sm">
          © 2025{" "}
          <a
            href="https://mirascope.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#E3735E] hover:underline"
          >
            Mirascope
          </a>
          . All rights reserved.
        </p>
      </div>
    ),
  },
  navigation: {
    prev: true,
    next: true,
  },
  project: {
    link: "https://github.com/Mirascope/mcp-community",
  },
  chat: {
    link: "https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA",
    icon: <SlackLogo width="18" height="18" />,
  },
  docsRepositoryBase:
    "https://github.com/Mirascope/mcp-community/tree/main/docs",
};
export default config;
