(function () {
  // ברירות מחדל יפות ל-DataTables (עברית, פריסה, עמוד=10)
  function extendDataTablesDefaults() {
    if (!window.jQuery || !$.fn.dataTable) return;
    $.extend(true, $.fn.dataTable.defaults, {
      language: { url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/he.json" },
      pageLength: 10,
      order: [],
      autoWidth: false,
      dom:
        "<'row align-items-center mb-2'<'col-auto'l><'col text-end'f>>" +
        "<'row'<'col-12'tr>>" +
        "<'row align-items-center mt-2'<'col'i><'col-auto'p>>"
    });
  }

  // אתחול טבלאות DataTables (מניעת init כפול)
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
        // guard עדין: responsive רק אם התוסף קיים
        responsive: !!($.fn.dataTable && $.fn.dataTable.Responsive)
        // שאר הברירות מחדל מגיעות מ-$.fn.dataTable.defaults (extend למעלה)
      });
    });
  }

  // תצוגת תמונה גדולה במודאל (lightbox)
  function initImagePreview() {
    // דילגציה – גם לתוכן שמוזרק דינמית
    $(document).on('click', '[data-image-preview]', function (e) {
      e.preventDefault();
      var src = $(this).attr('data-image-preview') || $(this).attr('src') || $(this).data('src');
      if (!src) return;
      var modal = document.getElementById('imageModal');
      if (!modal) return;
      var img = modal.querySelector('#modalImage') || modal.querySelector('#imageModalImg') || modal.querySelector('img');
      if (!img) return;
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

  // פלייסהולדר נחמד לשדה החיפוש של DT
  function initDtPlaceholder() {
    $(document).on('init.dt', function () {
      $('.dataTables_filter input').attr('placeholder', 'חפש טקסט…');
    });
  }

  // DOM Ready
  $(function () {
    extendDataTablesDefaults();
    initDataTables($(document));
    initImagePreview();
    initHtmxHooks();
    initTooltips();
    initDtPlaceholder();
  });
})();
