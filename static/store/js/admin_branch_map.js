(function(){
  // Only run on pages with latitude/longitude inputs
  document.addEventListener('DOMContentLoaded', function(){
    var latInput = document.getElementById('id_latitude');
    var lonInput = document.getElementById('id_longitude');
    if(!latInput || !lonInput) return;

    // Create container above the latitude input
    var container = document.createElement('div');
    container.id = 'branch-map-container';
    container.style.marginTop = '12px';

    var searchWrapper = document.createElement('div');
    searchWrapper.style.marginBottom = '6px';

    var searchInput = document.createElement('input');
    searchInput.type = 'search';
    searchInput.placeholder = 'Buscar dirección (Enter) — Nominatim (OpenStreetMap)';
    searchInput.style.width = '60%';
    searchInput.style.padding = '6px';
    searchInput.style.marginRight = '8px';

    var searchBtn = document.createElement('button');
    searchBtn.type = 'button';
    searchBtn.textContent = 'Buscar';
    searchBtn.style.padding = '6px 10px';

    searchWrapper.appendChild(searchInput);
    searchWrapper.appendChild(searchBtn);

    var mapDiv = document.createElement('div');
    mapDiv.id = 'branch-map';
    mapDiv.style.width = '100%';
    mapDiv.style.height = '360px';
    mapDiv.style.border = '1px solid #ddd';

    container.appendChild(searchWrapper);
    container.appendChild(mapDiv);

    // Insert after the latitude input's parent element
    var latWrapper = latInput.closest('.form-row') || latInput.parentElement;
    if(latWrapper && latWrapper.parentElement){
      latWrapper.parentElement.insertBefore(container, latWrapper.nextSibling);
    } else {
      latInput.parentElement.appendChild(container);
    }

    // Parse existing coords or use default (Mexico City)
    var lat = parseFloat(latInput.value) || 19.432608;
    var lon = parseFloat(lonInput.value) || -99.133209;

    // Initialize map when Leaflet is loaded
    function initMap(){
      if(typeof L === 'undefined'){
        // retry if leaflet not yet loaded
        setTimeout(initMap, 200);
        return;
      }

      var map = L.map('branch-map').setView([lat, lon], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      var marker = L.marker([lat, lon], {draggable:true}).addTo(map);

      function updateInputs(latlng){
        latInput.value = latlng.lat.toFixed(6);
        lonInput.value = latlng.lng.toFixed(6);
        // trigger change events if any listeners expect them
        latInput.dispatchEvent(new Event('change'));
        lonInput.dispatchEvent(new Event('change'));
      }

      marker.on('dragend', function(e){
        var pos = marker.getLatLng();
        updateInputs(pos);
      });

      map.on('click', function(e){
        marker.setLatLng(e.latlng);
        updateInputs(e.latlng);
      });

      // Search (Nominatim) — fetch first result
      function doSearch(q){
        if(!q) return;
        var url = 'https://nominatim.openstreetmap.org/search?format=json&limit=5&q=' + encodeURIComponent(q);
        // Nominatim requires a proper user-agent; browsers send one. We add &accept-language to help results
        fetch(url, {headers: {'Accept': 'application/json'}})
          .then(function(r){ return r.json(); })
          .then(function(results){
            if(results && results.length){
              var first = results[0];
              var newLat = parseFloat(first.lat);
              var newLon = parseFloat(first.lon);
              marker.setLatLng([newLat, newLon]);
              map.setView([newLat, newLon], 15);
              updateInputs({lat:newLat, lng:newLon});
              // Optionally fill address field if present
              var addressField = document.getElementById('id_address');
              if(addressField && first.display_name){
                addressField.value = first.display_name;
                addressField.dispatchEvent(new Event('change'));
              }
            } else {
              alert('No se encontraron resultados para: ' + q);
            }
          })
          .catch(function(err){
            console.error('Nominatim error', err);
            alert('Error buscando la dirección. Revisa la consola.');
          });
      }

      searchBtn.addEventListener('click', function(){ doSearch(searchInput.value); });
      searchInput.addEventListener('keypress', function(e){ if(e.key === 'Enter'){ e.preventDefault(); doSearch(searchInput.value); } });
    }

    initMap();
  });
})();
