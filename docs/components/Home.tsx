import { SlackLogo } from "@/components/SlackLogo";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useState, useEffect } from "react";
import { ArrowRight } from "lucide-react";

export const Home = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <main className="min-h-screen bg-white dark:bg-black overflow-x-hidden">
      {/* Modern Gradient Splash Background */}
      <div className="fixed inset-0 min-h-screen w-full overflow-hidden -z-10 pointer-events-none">
        {/* Main large terracotta blur at top right */}
        <div className="absolute -top-[10%] -right-[20%] w-[80vw] h-[80vw] rounded-full bg-gradient-to-bl from-[#E3735E]/15 to-transparent blur-[120px] dark:from-[#E3735E]/10 dark:to-transparent" />

        {/* Secondary blob bottom left */}
        <div className="absolute top-[60%] -left-[10%] w-[60vw] h-[60vw] rounded-full bg-gradient-to-tr from-[#E3735E]/10 to-transparent blur-[150px] dark:from-[#E3735E]/8 dark:to-transparent" />

        {/* Small accent in middle */}
        <div className="absolute top-[35%] right-[10%] w-[15vw] h-[15vw] rounded-full bg-[#E3735E]/10 blur-[80px] dark:bg-[#E3735E]/8" />

        {/* Tiny detail blobs */}
        <div className="absolute top-[20%] left-[15%] w-[5vw] h-[5vw] rounded-full bg-[#E3735E]/15 blur-[30px] dark:bg-[#E3735E]/10" />
        <div className="absolute top-[70%] right-[30%] w-[8vw] h-[8vw] rounded-full bg-[#E3735E]/10 blur-[40px] dark:bg-[#E3735E]/8" />

        {/* Additional blobs to ensure full coverage */}
        <div className="absolute bottom-[5%] left-[40%] w-[30vw] h-[30vw] rounded-full bg-gradient-to-tr from-[#E3735E]/8 to-transparent blur-[100px] dark:from-[#E3735E]/6 dark:to-transparent" />
        <div className="absolute -bottom-[10%] right-[15%] w-[25vw] h-[25vw] rounded-full bg-[#E3735E]/5 blur-[80px] dark:bg-[#E3735E]/4" />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 py-16 md:py-24 flex flex-col gap-10 items-center justify-center text-center px-6 max-w-6xl mx-auto">
        <div
          className={`transform transition-all duration-700 ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
          }`}
        >
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black mb-6 bg-clip-text text-transparent bg-gradient-to-r from-[#E3735E] to-[#E3735E]/80">
            MCP Community
          </h1>
          <p className="text-xl sm:text-2xl max-w-3xl mx-auto text-gray-700 dark:text-gray-300 mb-10">
            Easily implement, deploy, and use MCP servers
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              asChild
              variant="outline"
              size="lg"
              className="px-8 py-6 rounded-lg text-base font-medium border-[#E3735E]/20 hover:bg-[#E3735E]/5"
            >
              <Link href="/docs/quickstart">
                Get Started
                <ArrowRight />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-20 px-6 max-w-7xl mx-auto">
        <div
          className={`grid grid-cols-1 md:grid-cols-3 gap-8 transform transition-all duration-700 ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
          }`}
          style={{ transitionDelay: "200ms" }}
        >
          <Link href="/docs/server" className="block cursor-pointer">
            <div className="bg-white/50 dark:bg-black/50 p-8 rounded-xl border border-gray-200 dark:border-gray-800 backdrop-blur-sm hover:shadow-lg transition-all hover:border-[#E3735E]/30 group">
              <div className="w-12 h-12 bg-[#E3735E]/10 rounded-lg flex items-center justify-center mb-6 group-hover:bg-[#E3735E]/20 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#E3735E"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect x="5" y="2" width="14" height="20" rx="2" ry="2" />
                  <line x1="12" y1="18" x2="12.01" y2="18" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3">Simple MCP Servers</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Easily implement an MCP server using SimpleMCP.
              </p>
            </div>
          </Link>

          <Link href="/docs/deployment" className="block cursor-pointer">
            <div className="bg-white/50 dark:bg-black/50 p-8 rounded-xl border border-gray-200 dark:border-gray-800 backdrop-blur-sm hover:shadow-lg transition-all hover:border-[#E3735E]/30 group">
              <div className="w-12 h-12 bg-[#E3735E]/10 rounded-lg flex items-center justify-center mb-6 group-hover:bg-[#E3735E]/20 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#E3735E"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" />
                  <path d="M12 3v1" />
                  <path d="M12 20v1" />
                  <path d="M3 12h1" />
                  <path d="M20 12h1" />
                  <path d="M18.364 5.636l-.707.707" />
                  <path d="M6.343 17.657l-.707.707" />
                  <path d="M5.636 5.636l.707.707" />
                  <path d="M17.657 17.657l.707.707" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3">One-Click Deployment</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Deploy your MCP server with a single click.
              </p>
            </div>
          </Link>

          <Link href="/docs/client" className="block cursor-pointer">
            <div className="bg-white/50 dark:bg-black/50 p-8 rounded-xl border border-gray-200 dark:border-gray-800 backdrop-blur-sm hover:shadow-lg transition-all hover:border-[#E3735E]/30 group">
              <div className="w-12 h-12 bg-[#E3735E]/10 rounded-lg flex items-center justify-center mb-6 group-hover:bg-[#E3735E]/20 transition-colors">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#E3735E"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                  <line x1="8" y1="21" x2="16" y2="21" />
                  <line x1="12" y1="17" x2="12" y2="21" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3">
                Standard Chat Interface
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Connect and use MCP servers in chat UI interface.
              </p>
            </div>
          </Link>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-20 px-6 max-w-4xl mx-auto">
        <div
          className={`transform transition-all duration-700 ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
          }`}
          style={{ transitionDelay: "600ms" }}
        >
          <div className="bg-gradient-to-r from-[#E3735E]/20 to-[#E3735E]/10 dark:from-[#E3735E]/10 dark:to-black/20 p-10 rounded-2xl text-center backdrop-blur-sm border border-[#E3735E]/20 shadow-md">
            <h2 className="text-2xl md:text-3xl font-bold mb-6">
              Join the MCP Community
            </h2>
            <p className="text-gray-700 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
              Be part of the growing ecosystem of MCP servers and applications.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                asChild
                variant="default"
                size="lg"
                className="px-8 py-6 rounded-lg text-base font-medium"
              >
                <a
                  href="https://github.com/Mirascope/mcp-community"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="mr-2"
                  >
                    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path>
                    <path d="M9 18c-4.51 2-5-2-7-2"></path>
                  </svg>
                  Star on GitHub
                </a>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="px-8 py-6 rounded-lg text-base font-medium bg-white/70 dark:bg-transparent"
              >
                <a
                  href="https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <SlackLogo width="20" height="20" />
                  Community
                </a>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};
