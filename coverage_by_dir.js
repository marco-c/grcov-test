(function() {
  /**
   * Approssimazione decimale di un numero.
   *
   * @param {String}  type  Il tipo di approssimazione.
   * @param {Number}  value Il numero.
   * @param {Integer} exp   L'esponente (the 10 logarithm of the adjustment base).
   * @returns {Number} Il valore approssimato.
   */
  function decimalAdjust(type, value, exp) {
    // Se exp è undefined o zero...
    if (typeof exp === 'undefined' || +exp === 0) {
      return Math[type](value);
    }
    value = +value;
    exp = +exp;
    // Se value non è un numero o exp non è un intero...
    if (isNaN(value) || !(typeof exp === 'number' && exp % 1 === 0)) {
      return NaN;
    }
    // Se value è negativo...
    if (value < 0) {
      return -decimalAdjust(type, -value, exp);
    }
    // Shift
    value = value.toString().split('e');
    value = Math[type](+(value[0] + 'e' + (value[1] ? (+value[1] - exp) : -exp)));
    // Shift back
    value = value.toString().split('e');
    return +(value[0] + 'e' + (value[1] ? (+value[1] + exp) : exp));
  }

  // Decimal round
  if (!Math.round10) {
    Math.round10 = function(value, exp) {
      return decimalAdjust('round', value, exp);
    };
  }
  // Decimal floor
  if (!Math.floor10) {
    Math.floor10 = function(value, exp) {
      return decimalAdjust('floor', value, exp);
    };
  }
  // Decimal ceil
  if (!Math.ceil10) {
    Math.ceil10 = function(value, exp) {
      return decimalAdjust('ceil', value, exp);
    };
  }
})();

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

  let previous_column = row.insertCell(2);
  previous_column.appendChild(document.createTextNode(obj['prev'].toFixed(2)));

  let diff_column = row.insertCell(3);
  let diff_val = Math.round10(obj['cur'] - obj['prev'], -2);
  let diff = document.createElement('span');
  diff.textContent = diff_val;
  if (diff_val >= 0) {
    diff.style.backgroundColor = 'green';
  } else {
    diff.style.backgroundColor = 'red';
  }
  diff.style.color = 'white';
  diff_column.appendChild(diff);
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
