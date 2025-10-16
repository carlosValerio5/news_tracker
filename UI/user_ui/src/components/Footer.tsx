function Footer({ fixed }: { fixed?: boolean }) {
  return (
    <footer className={`w-full bg-gray-100 text-gray-600 text-center py-6 border-t border-gray-300 mt-1.5 ${fixed ? 'fixed bottom-0 left-0' : ''}`}>
      <div className="flex items-center justify-center gap-2 md:justify-evenly mb-10">
        <p className="text-sm md:text-lg font-semibold">NewsTracker</p>
        <div className="mb-2 hidden grid-cols-2 gap-3 items-center md:pr-20">
          <a href="/about" className="text-xs mx-2 hover:underline md:text-sm">
            About
          </a>
          <a
            href="/privacy"
            className="text-xs mx-2 hover:underline md:text-sm"
          >
            Privacy Policy
          </a>
          <a href="/terms" className="text-xs mx-2 hover:underline md:text-sm">
            Terms of Service
          </a>
          <a
            href="/contact"
            className="text-xs mx-2 hover:underline md:text-sm"
          >
            Contact
          </a>
        </div>
      </div>
      <div className="text-xs">© 2025 News Tracker. All rights reserved.</div>
    </footer>
  );
}

export default Footer;
