function SearchBar() {
  return (
    <div className="w-11/12 sm:w-64">
      <input
        type="text"
        placeholder="Search news..."
        className="w-full p-2 border border-black bg-white text-black placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black mb-2 rounded-xl"
      />
    </div>
  );
}

export default SearchBar;
