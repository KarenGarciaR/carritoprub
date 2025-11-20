(function(){
  document.addEventListener('DOMContentLoaded', function(){
    // Collect branches from DOM cards
    var cardEls = Array.from(document.querySelectorAll('.branch-card'));
    var branches = cardEls.map(function(el){
      var lat = parseFloat(el.dataset.lat);
      var lon = parseFloat(el.dataset.lon);
      return {
        id: el.dataset.branchId,
        name: el.querySelector('h3') ? el.querySelector('h3').innerText.trim() : '',
        address: el.querySelector('p') ? el.querySelector('p').innerText.trim() : '',
        lat: isFinite(lat) ? lat : null,
        lon: isFinite(lon) ? lon : null,
        el: el
      };
    }).filter(function(b){ return b.lat !== null && b.lon !== null; });

    var mapContainer = document.getElementById('public-branches-map');
    if(!mapContainer) return;

    // default center (Mexico) if no branches
    var defaultLat = 23.6345, defaultLon = -102.5528, defaultZoom = 5;
    var map = L.map(mapContainer).setView([defaultLat, defaultLon], defaultZoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    var markers = {};
    if(branches.length){
      var bounds = [];
      branches.forEach(function(b){
        var marker = L.marker([b.lat, b.lon]).addTo(map);
        var popupHtml = '<strong>'+escapeHtml(b.name)+'</strong><br/>'+escapeHtml(b.address)+'<br/>';
        popupHtml += '<a href="#" onclick="return false;">Cómo llegar</a>';
        marker.bindPopup(popupHtml);
        markers[b.id] = marker;
        bounds.push([b.lat, b.lon]);

        // clicking card centers map
        b.el.addEventListener('click', function(e){
          // avoid when clicking internal buttons handled below
          if(e.target && e.target.classList && e.target.classList.contains('btn-center-map')) return;
          map.setView([b.lat, b.lon], 15);
          marker.openPopup();
          scrollToMap();
        });

        // 'Ver en mapa' button
        var btn = b.el.querySelector('.btn-center-map');
        if(btn){
          btn.addEventListener('click', function(ev){
            ev.preventDefault();
            map.setView([b.lat, b.lon], 15);
            marker.openPopup();
            scrollToMap();
          });
        }
      });
      try{
        map.fitBounds(bounds, {padding:[40,40]});
      }catch(e){
        // fallback
        map.setView([branches[0].lat, branches[0].lon], 12);
      }
    }

    function scrollToMap(){
      if(!mapContainer) return;
      mapContainer.scrollIntoView({behavior:'smooth', block:'center'});
    }

    function escapeHtml(s){
      if(!s) return '';
      return s.replace(/[&"'<>]/g, function(c){
        return {'&':'&amp;','"':'&quot;',"'":"&#39;","<":"&lt;",">":"&gt;"}[c];
      });
    }

  });
})();
