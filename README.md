# Wikipedia Knowledge Explorer

A prototype that retrieves Wikipedia articles, clusters them based on content similarity, generates summaries, and visualizes the results on a front-end web interface.

---

## Description

This project allows users to:
1. Enter a search term.
2. Fetch relevant article titles from Wikipedia.
3. Group these articles using a clustering algorithm (K-Means).
4. Generate a short summary for each article.
5. Display results and visualize clusters on a webpage.

---

## Basic Features

- [x] User can type in a keyword to search Wikipedia.
- [x] Articles are retrieved via the Wikipedia API.
- [ ] Simple K-Means clustering groups the articles by content similarity.
- [ ] Articles are summarized using a text summarization library (e.g., sumy).
- [ ] Frontend displays article titles, summaries, and indicates cluster labels.
- [ ] Basic static graph visualization with D3.js (nodes colored by cluster).

---

## Additional Features (Optional / Future Enhancements)

- [ ] Use GPT-3 or other advanced models for more sophisticated summarization.
- [ ] Support dynamic or interactive graph layouts (e.g., force-directed graphs with dragging).
- [ ] Add topic labeling to clusters (e.g., detect a phrase that describes each cluster).
- [ ] Implement advanced search and filtering (e.g., search by date, popularity).
- [ ] Provide interactive tooltips with larger previews or images.

---

## Project Roles and Tasks

### Backend Developer 1
1. **FastAPI Setup & Configuration**
   - Create a FastAPI application to handle incoming requests.
   - Ensure the server can run (e.g., uvicorn main:app --reload).

2. **Wikipedia API Integration**
   - Retrieve article titles and content based on user search terms.
   - Handle any pagination or error-checking from the Wikipedia API.

3. **Clustering**
   - Convert article text into a vector form (e.g., TF-IDF).
   - Implement basic K-Means clustering using scikit-learn.
   - Store the cluster labels for each article.

---

### Backend Developer 2
1. **Text Summarization**
   - Use sumy (or GPT-based) summarization to generate concise summaries for each article.
   - Validate the length and quality of each summary.

2. **Combine and Return Results**
   - Consolidate data (titles, summaries, cluster labels) into a JSON response.
   - Structure the output as needed for the frontend (e.g., { "articles": [...], "searchTerm": "..." }).

3. **Documentation & Integration**
   - Provide clear documentation on API endpoints and JSON formats.
   - Ensure the integration with Developer 1’s clustering results is seamless.

---

### Frontend Developer 1
1. **UI & Layout**
   - Create a simple HTML page with a text input and “Search” button.
   - Use CSS to style the form, buttons, and general layout.

2. **API Requests & Data Handling**
   - Use Axios (or fetch) to send the user’s query to the backend.
   - Display the returned article list with basic cluster info or labels.

3. **User Interaction**
   - Provide feedback during loading (e.g., “Fetching articles…”).
   - Handle errors gracefully (e.g., no articles found, server not responding).

---

### Frontend Developer 2
1. **D3.js Graph Visualization**
   - Implement a (static) graph layout where each article is a node.
   - Different colors indicate different cluster labels.

2. **Tooltip & Hover Effects**
   - Show the article’s title (and possibly summary) on hover.
   - Maintain readability and responsive design.

3. **Integration & Updates**
   - Ensure visualization updates or re-renders when new articles are fetched.
   - Coordinate with Developer 1’s UI components to share data seamlessly.
