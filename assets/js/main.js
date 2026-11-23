// MadaDrive — menu mobile + formulaires de devis envoyés sur WhatsApp
(function () {
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Chaque formulaire .js-quote ouvre WhatsApp avec la demande déjà rédigée.
  // Le navigateur vérifie d'abord les champs obligatoires (attribut required).
  document.querySelectorAll('form.js-quote').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var number = form.getAttribute('data-wa');
      var get = function (name) {
        var el = form.elements[name];
        return el && el.value ? el.value.trim() : '';
      };
      var frDate = function (v) {
        var d = v.split('-');
        return d.length === 3 ? d[2] + '/' + d[1] + '/' + d[0] : v;
      };

      var lines = ['*DEMANDE CLIENT – MadaDrive*', ''];
      if (get('service')) lines.push('• Prestation : ' + get('service'));
      if (get('depart')) lines.push('• Départ : ' + get('depart'));
      if (get('destination')) lines.push('• Destination : ' + get('destination'));
      if (get('date')) lines.push('• Date : ' + frDate(get('date')));
      if (get('jours')) lines.push('• Nombre de jours : ' + get('jours'));
      if (get('mois')) lines.push('• Durée : ' + get('mois') + ' mois');
      if (get('passagers')) lines.push('• Passagers : ' + get('passagers'));
      if (get('message')) lines.push('• Précisions : ' + get('message'));

      lines.push('', '*Contact du client*');
      if (get('nom')) lines.push('• Nom : ' + get('nom'));
      if (get('contact')) lines.push('• Interlocuteur : ' + get('contact'));
      if (get('tel')) lines.push('• Téléphone / WhatsApp : ' + get('tel'));
      if (get('email')) lines.push('• E-mail : ' + get('email'));
      lines.push('• Envoyé depuis : ' + document.title.split('|')[0].trim());

      var url = 'https://wa.me/' + number + '?text=' + encodeURIComponent(lines.join('\n'));
      window.open(url, '_blank', 'noopener');
    });
  });

  // Date minimum = aujourd'hui
  var today = new Date().toISOString().slice(0, 10);
  document.querySelectorAll('input[type=date]').forEach(function (i) { i.min = today; });
})();
