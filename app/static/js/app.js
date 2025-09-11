(function () {
  // אתחול טבלאות DataTables רק אם לא אופסו כבר
  function initDataTables(ctx) {
    var $root = ctx && ctx.jquery ? ctx : $(document);
    var $tables = $root.find('table.js-datatable');
    $tables.each(function () {
      var $t = $(this);
      if ($.fn.dataTable.isDataTable($t)) return;
      $t.DataTable({
        paging: true,
        searching: true,
        ordering: true,
        autoWidth: false,
        responsive: true,
        language: { url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/he.json" }
      });
    });
  }

  // תצוגת תמונה גדולה במודאל (lightbox) – לשימוש בהמשך
  function initImagePreview() {
    // דילגציה – גם לתוכן שמוזרק דינמית
    $(document).on('click', '[data-image-preview]', function (e) {
      e.preventDefault();
      var src = $(this).attr('data-image-preview') || $(this).attr('src') || $(this).data('src');
      if (!src) return;
      var modal = document.getElementById('imageModal');
      if (!modal) return;
      var img = modal.querySelector('#imageModalImg');
      img.src = src;
      var modalObj = bootstrap.Modal.getOrCreateInstance(modal);
      modalObj.show();
    });
  }

  // HTMX: אחרי החלפת תוכן – לאתחל שוב טבלאות באזור שהוחלף
  function initHtmxHooks() {
    document.body.addEventListener('htmx:afterSwap', function (evt) {
      initDataTables($(evt.target));
    });
  }

  // Bootstrap Tooltips
  function initTooltips() {
    var nodes = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    nodes.forEach(function (el) { new bootstrap.Tooltip(el); });
  }

  // DOM Ready
  $(function () {
    initDataTables($(document));
    initImagePreview();
    initHtmxHooks();
    initTooltips();
  });
})();
