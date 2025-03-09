import meta from "../../../pages/_meta.ts";
import docs_meta from "../../../pages/docs/_meta.tsx";
import self_hosting_meta from "../../../pages/self-hosting/_meta.tsx";
export const pageMap = [{
  data: meta
}, {
  name: "404",
  route: "/404",
  frontMatter: {
    "sidebarTitle": "404"
  }
}, {
  name: "docs",
  route: "/docs",
  children: [{
    data: docs_meta
  }, {
    name: "client",
    route: "/docs/client",
    frontMatter: {
      "sidebarTitle": "Client"
    }
  }, {
    name: "deployment",
    route: "/docs/deployment",
    frontMatter: {
      "sidebarTitle": "Deployment"
    }
  }, {
    name: "index",
    route: "/docs",
    frontMatter: {
      "sidebarTitle": "Index"
    }
  }, {
    name: "open-source",
    route: "/docs/open-source",
    frontMatter: {
      "sidebarTitle": "Open Source"
    }
  }, {
    name: "quickstart",
    route: "/docs/quickstart",
    frontMatter: {
      "sidebarTitle": "Quickstart"
    }
  }, {
    name: "server",
    route: "/docs/server",
    frontMatter: {
      "sidebarTitle": "Server"
    }
  }]
}, {
  name: "index",
  route: "/",
  frontMatter: {
    "title": "MCP Community",
    "description": "Community Built MCP Servers -- Deploy in one click."
  }
}, {
  name: "self-hosting",
  route: "/self-hosting",
  children: [{
    data: self_hosting_meta
  }, {
    name: "index",
    route: "/self-hosting",
    frontMatter: {
      "sidebarTitle": "Index"
    }
  }]
}];