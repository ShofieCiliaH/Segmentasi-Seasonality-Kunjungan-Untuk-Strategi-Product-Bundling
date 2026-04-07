document.addEventListener("DOMContentLoaded", () => {
  const fileInputs = document.querySelectorAll("[data-file-input]");

  fileInputs.forEach((input) => {
    const feedback = input
      .closest("form")
      ?.querySelector("[data-file-feedback]");

    input.addEventListener("change", () => {
      if (!feedback) {
        return;
      }

      const selected = input.files && input.files.length > 0 ? input.files[0].name : "";
      feedback.textContent = selected
        ? `File terpilih: ${selected}`
        : "Pilih file transaksi untuk memulai proses analisis.";
    });
  });

  if (window.bootstrap) {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((element) => {
      new window.bootstrap.Tooltip(element);
    });
  }
});
