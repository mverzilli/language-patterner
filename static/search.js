/* language-patterner client-side search */
(function () {
  "use strict";

  var input = document.getElementById("search-input");
  var resultsContainer = document.getElementById("search-results");
  if (!input || !resultsContainer) return;

  var index = null;
  var rootPrefix = window.ROOT_PREFIX || "";

  // Load the search index
  fetch(window.SEARCH_INDEX_URL || "search-index.json")
    .then(function (res) { return res.json(); })
    .then(function (data) { index = data; })
    .catch(function () { /* silently fail if no index */ });

  function normalize(str) {
    return (str || "").toLowerCase().trim();
  }

  function matches(pattern, query) {
    var q = normalize(query);
    if (!q) return false;
    var terms = q.split(/\s+/);
    var haystack = [
      String(pattern.number),
      normalize(pattern.name),
      normalize(pattern.problem),
      (pattern.tags || []).map(normalize).join(" "),
      normalize(pattern.scale),
    ].join(" ");
    return terms.every(function (term) {
      return haystack.indexOf(term) !== -1;
    });
  }

  function render(results) {
    if (results.length === 0) {
      resultsContainer.innerHTML = '<div class="search-no-results">No patterns found</div>';
      resultsContainer.hidden = false;
      return;
    }

    var html = results.slice(0, 20).map(function (p) {
      var problem = p.problem ? p.problem.substring(0, 100) : "";
      if (problem.length === 100) problem += "...";
      return (
        '<a href="' + rootPrefix + 'pattern/' + p.number + '.html">' +
          '<span class="result-number">' + p.number + '</span>' +
          '<span class="result-name">' + escapeHtml(p.name) + '</span>' +
          (problem ? '<span class="result-problem">' + escapeHtml(problem) + '</span>' : '') +
        '</a>'
      );
    }).join("");

    resultsContainer.innerHTML = html;
    resultsContainer.hidden = false;
  }

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  input.addEventListener("input", function () {
    var query = input.value;
    if (!query.trim() || !index) {
      resultsContainer.hidden = true;
      resultsContainer.innerHTML = "";
      return;
    }
    var results = index.filter(function (p) { return matches(p, query); });
    render(results);
  });

  // Close on click outside
  document.addEventListener("click", function (e) {
    if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
      resultsContainer.hidden = true;
    }
  });

  // Reopen on focus if there's a query
  input.addEventListener("focus", function () {
    if (input.value.trim() && index) {
      input.dispatchEvent(new Event("input"));
    }
  });
})();
