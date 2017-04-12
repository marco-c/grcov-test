let onLoad = new Promise(function(resolve, reject) {
  window.onload = resolve;
});

function getCoverage() {
  return fetch('coverage_by_dir.json')
  .then(response => response.json());
}

function addRow(dir, obj) {
  let table = document.getElementById('table');

  let row = table.insertRow(table.rows.length);

  let directory_column = row.insertCell(0);
  let directory_link = document.createElement('a');
  directory_link.href = '?dir=' + dir;
  directory_link.appendChild(document.createTextNode(dir + '/'))
  directory_column.appendChild(directory_link);

  let current_column = row.insertCell(1);
  current_column.appendChild(document.createTextNode(obj['cur'].toFixed(2)));

  let previous_column = row.insertCell(1);
  previous_column.appendChild(document.createTextNode(obj['prev'].toFixed(2)));
}

function buildTable() {
  let queryVars = new URL(location.href).search.substring(1).split('&');
  let rootDir = '';
  for (let queryVar of queryVars) {
      if (queryVar.startsWith('dir=')) {
          rootDir = queryVar.substring(('dir=').length).trim();
      }
  }

  function isDir(dirName) {
      if (rootDir == '') {
          return !dirName.includes('/');
      }

      return rootDir != dirName && dirName.startsWith(rootDir);
  }

  getCoverage()
  .then(data => {
    let dirs = Object.keys(data);
    dirs
    .filter(dirName => isDir(dirName))
    .sort()
    .forEach(dirName => addRow(dirName, data[dirName]));
  });
}

function rebuildTable() {
  let table = document.getElementById('table');

  while(table.rows.length > 1) {
    table.deleteRow(table.rows.length - 1);
  }

  buildTable();
}

onLoad
.then(function() {
  buildTable();
})
.catch(function(err) {
  console.error(err);
});
