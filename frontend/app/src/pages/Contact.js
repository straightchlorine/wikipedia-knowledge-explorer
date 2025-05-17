const About = () => {
  return (
    <section className="p-6 md:p-12 bg-white rounded-2xl shadow-lg max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-4 text-gray-900">About the Project</h1>
      <p className="text-lg text-gray-700 mb-4">
        <strong>Wikipedia Knowledge Explorer</strong> is a student project developed as part of an academic course.
        It was implemented by a project group with the goal of applying practical knowledge in web development,
        machine learning, and data visualization.
      </p>
      <p className="text-gray-700">
        The application is designed to help users explore Wikipedia content by retrieving related articles,
        clustering them based on content similarity, summarizing key information, and visualizing the results
        in an interactive interface.
      </p>
    </section>
  );
};

export default About;
