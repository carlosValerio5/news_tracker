import React, { useState } from "react";
import SearchBar from "./SearchBar";
import RegisterButton from "./RegisterButton";
import { Link } from "react-router";

const NavBar: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="w-full flex flex-col sm:flex-row items-center p-4 bg-white text-black relative">
      {/* Logo and Hamburger */}
      <div className="w-full flex items-center justify-between sm:justify-start mb-2 sm:mb-0">
        <div className="text-sm sm:text-xl"><Link to="/">NewsTracker</Link></div>
        {/* Hamburger icon for mobile */}
        <button
          className="sm:hidden p-2 focus:outline-none"
          aria-label="Toggle menu"
          onClick={() => setMenuOpen((open) => !open)}
        >
            {menuOpen ? (
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            ) : (
                <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            )}
        </button>
      </div>

      {/* Right-aligned section for desktop */}
      <div className="hidden sm:flex w-full sm:w-auto flex-col sm:flex-row items-center sm:justify-end gap-2 sm:gap-6 ml-auto">
        {/* Search Field */}
        <SearchBar />
        {/* News Section */}
        <Link to="/news" className="text-gray-400 text-base px-2 py-1 rounded hover:bg-black hover:text-white transition">News</Link>
        {/* Register Button */}
        <RegisterButton type="SECONDARY" />
      </div>

      {/* Dropdown menu for mobile */}
      {menuOpen && (
        <div className="sm:hidden absolute top-full left-0 w-full bg-white shadow-md z-10 flex flex-col items-center gap-2 py-4">
          <SearchBar />
          <Link to="/news" className="text-gray-400 text-base px-2 py-1 rounded hover:bg-black hover:text-white transition w-11/12 text-center">News</Link>
          <RegisterButton type="SECONDARY" />
        </div>
      )}
    </nav>
  );
};

export default NavBar;