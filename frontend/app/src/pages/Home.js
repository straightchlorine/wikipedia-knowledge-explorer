const Home = () => (
  <section className="p-6 md:p-12 bg-white rounded-2xl shadow-lg max-w-4xl mx-auto">
    <h1 className="text-3xl font-bold mb-4 text-gray-900">
      Wikipedia Knowledge Explorer
    </h1>
    <p className="text-lg text-gray-700 mb-6">
      <strong>Wikipedia Knowledge Explorer</strong> is an interactive prototype that helps users explore and understand related topics on Wikipedia through intelligent clustering, summarization, and visualization.
    </p>
    <h2 className="text-2xl font-semibold mb-2 text-gray-800">What it does</h2>
    <ul className="list-disc list-inside text-gray-700 mb-6">
      <li>Users enter a search term to query Wikipedia.</li>
      <li>The system retrieves relevant articles and groups them using a K-Means clustering algorithm.</li>
      <li>Each article is automatically summarized to provide quick insights.</li>
      <li>Results are displayed on a clean, intuitive frontend, including an interactive graph showing topic clusters.</li>
    </ul>
    <h2 className="text-2xl font-semibold mb-2 text-gray-800">Project Goal</h2>
    <p className="text-gray-700">
      The goal of this project is to make information discovery easier by surfacing structured, clustered, and summarized knowledge from Wikipedia. Whether you're doing research or casually exploring, this tool helps you understand topic relationships and dive deeper into specific areas of interest.
    </p>
  </section>
);

export default Home;
