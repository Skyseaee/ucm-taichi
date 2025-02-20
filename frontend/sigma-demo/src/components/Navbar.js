import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  // 切换移动端菜单的显示状态
  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <nav className="bg-gray-800 shadow sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link to="/" className="text-white text-xl font-bold">
              Your Logo
            </Link>
          </div>

          {/* 桌面端菜单 */}
          <div className="hidden md:flex gap-4">
            <Link
                to="/"
                className="bg-gray-700 text-white hover:bg-gray-600 px-4 py-2 rounded-md font-medium transition duration-300"
            >
                Home
            </Link>
            <Link
                to="/about"
                className="bg-gray-700 text-white hover:bg-gray-600 px-4 py-2 rounded-md font-medium transition duration-300"
            >
                About
            </Link>
            <Link
                to="/services"
                className="bg-gray-700 text-white hover:bg-gray-600 px-4 py-2 rounded-md font-medium transition duration-300"
            >
                Services
            </Link>
            </div>


          {/* 移动端菜单按钮 */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-gray-300 hover:text-white focus:outline-none transition-colors duration-300"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {isOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* 移动端下拉菜单 */}
      {isOpen && (
        <div className="md:hidden px-2 pb-3 space-y-1 transition-all duration-300">
          <Link
            to="/"
            onClick={() => setIsOpen(false)}
            className="block text-gray-300 hover:text-white px-3 py-2 rounded-md transition-colors duration-300"
          >
            Home
          </Link>
          <Link
            to="/about"
            onClick={() => setIsOpen(false)}
            className="block text-gray-300 hover:text-white px-3 py-2 rounded-md transition-colors duration-300"
          >
            About
          </Link>
          <Link
            to="/services"
            onClick={() => setIsOpen(false)}
            className="block text-gray-300 hover:text-white px-3 py-2 rounded-md transition-colors duration-300"
          >
            Services
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
