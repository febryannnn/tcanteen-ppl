# TCanteen: Sistem Pemesanan Kantin Teknik Informatika ITS
# Implementasi Repository Pattern (Python)
# PPL D11

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from enum import Enum
from reportlab.pdfgen import canvas
from openpyxl import Workbook

# Section 1: Model Entity
class StatusPesanan(Enum):
    # Enum untuk status pesanan yang valid.
    menunggu    = "menunggu"
    diterima    = "diterima"
    diproses    = "diproses"
    siap_diambil = "Siap Diambil"
    selesai     = "selesai"
    Ditolak     = "Ditolak"

class Menu:
    # Model data untuk item menu di kantin
    def __init__(self, id: int, nama: str, harga: float, tersedia: bool = True):
        self.id       = id
        self.nama     = nama
        self.harga    = harga
        self.tersedia = tersedia

    def __repr__(self):
        status = "Tersedia" if self.tersedia else "Habis"
        return f"Menu(id={self.id}, nama='{self.nama}', harga=Rp{self.harga:,.0f}, status={status})"

class ItemPesanan:
    # Model data untuk satu item dalam sebuah pesanan.
    def __init__(self, menu: Menu, jumlah: int):
        self.menu   = menu
        self.jumlah = jumlah

    @property
    def subtotal(self) -> float:
        return self.menu.harga * self.jumlah

    def __repr__(self):
        return f"  - {self.menu.nama} x{self.jumlah} = Rp{self.subtotal:,.0f}"


class Pesanan:
    # Model data untuk satu pesanan pelanggan.
    def __init__(self, id: int, nama_pelanggan: str, items: List[ItemPesanan],
                 jenis_penyajian: str = "Dine In"):
        self.id               = id
        self.nama_pelanggan   = nama_pelanggan
        self.items            = items
        self.jenis_penyajian  = jenis_penyajian
        self.status           = StatusPesanan.menunggu
        self.waktu_pesanan    = datetime.now()

    @property
    def total_harga(self) -> float:
        return sum(item.subtotal for item in self.items)

    def __repr__(self):
        return (f"Pesanan(id={self.id}, pelanggan='{self.nama_pelanggan}', "
                f"total=Rp{self.total_harga:,.0f}, status={self.status.value})")


class Transaksi:
    # Model data untuk laporan keuangan / transaksi.
    def __init__(self, id: int, pesanan: Pesanan, tanggal: datetime = None):
        self.id          = id
        self.pesanan     = pesanan
        self.total_bayar = pesanan.total_harga
        self.tanggal     = tanggal or datetime.now()

    def __repr__(self):
        return (f"Transaksi(id={self.id}, pesanan_id={self.pesanan.id}, "
                f"total=Rp{self.total_bayar:,.0f}, tanggal={self.tanggal.strftime('%Y-%m-%d')})")


# Section 2: Interface (Abstract Repository)
class IPesananRepository(ABC):
    # Interface kontrak untuk semua operasi data Pesanan.
    @abstractmethod
    def get_all(self) -> List[Pesanan]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Pesanan]:
        pass

    @abstractmethod
    def add(self, pesanan: Pesanan) -> None:
        pass

    @abstractmethod
    def update_status(self, id: int, status: StatusPesanan) -> bool:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass


class IMenuRepository(ABC):
    # Interface kontrak untuk semua operasi data Menu.
    @abstractmethod
    def get_all(self) -> List[Menu]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Menu]:
        pass

    @abstractmethod
    def add(self, menu: Menu) -> None:
        pass

    @abstractmethod
    def update(self, menu: Menu) -> bool:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass


class ITransaksiRepository(ABC):
    # Interface kontrak untuk semua operasi data Transaksi.
    @abstractmethod
    def get_all(self) -> List[Transaksi]:
        pass

    @abstractmethod
    def get_by_periode(self, mulai: datetime, akhir: datetime) -> List[Transaksi]:
        pass

    @abstractmethod
    def add(self, transaksi: Transaksi) -> None:
        pass

    @abstractmethod
    def get_total_pendapatan(self, mulai: datetime, akhir: datetime) -> float:
        pass


# Section 3: Concreate Repository (Implementasi In-Memory)
# Simulasi database menggunakan list Python
class PesananRepository(IPesananRepository):
    # Implementasi konkret IPesananRepository.
    # Menyimpan data pesanan di memori (simulasi database).
    def __init__(self):
        self._storage: List[Pesanan] = []

    def get_all(self) -> List[Pesanan]:
        # Mengambil seluruh data pesanan dari storage.
        return list(self._storage)

    def get_by_id(self, id: int) -> Optional[Pesanan]:
        # Mencari pesanan berdasarkan ID; kembalikan None jika tidak ditemukan.
        for pesanan in self._storage:
            if pesanan.id == id:
                return pesanan
        return None

    def add(self, pesanan: Pesanan) -> None:
        # Menyimpan pesanan baru ke storage.
        self._storage.append(pesanan)

    def update_status(self, id: int, status: StatusPesanan) -> bool:
        # Memperbarui status pesanan; kembalikan True jika berhasil.
        pesanan = self.get_by_id(id)
        if pesanan:
            pesanan.status = status
            return True
        return False

    def delete(self, id: int) -> bool:
        # Menghapus pesanan dari storage berdasarkan ID.
        pesanan = self.get_by_id(id)
        if pesanan:
            self._storage.remove(pesanan)
            return True
        return False


class MenuRepository(IMenuRepository):
    # Implementasi konkret IMenuRepository.
    # Menyimpan data menu di memori (simulasi database).

    def __init__(self):
        self._storage: List[Menu] = []

    def get_all(self) -> List[Menu]:
        return list(self._storage)

    def get_by_id(self, id: int) -> Optional[Menu]:
        for menu in self._storage:
            if menu.id == id:
                return menu
        return None

    def add(self, menu: Menu) -> None:
        self._storage.append(menu)

    def update(self, menu: Menu) -> bool:
        # Memperbarui data menu yang sudah ada berdasarkan ID.
        existing = self.get_by_id(menu.id)
        if existing:
            existing.nama     = menu.nama
            existing.harga    = menu.harga
            existing.tersedia = menu.tersedia
            return True
        return False

    def delete(self, id: int) -> bool:
        menu = self.get_by_id(id)
        if menu:
            self._storage.remove(menu)
            return True
        return False


class TransaksiRepository(ITransaksiRepository):
    # Implementasi konkret ITransaksiRepository
    # Menyimpan data transaksi di memori (simulasi database)

    def __init__(self):
        self._storage: List[Transaksi] = []

    def get_all(self) -> List[Transaksi]:
        return list(self._storage)

    def get_by_periode(self, mulai: datetime, akhir: datetime) -> List[Transaksi]:
        # "Memfilter transaksi berdasarkan rentang tanggal
        return [
            t for t in self._storage
            if mulai <= t.tanggal <= akhir
        ]

    def add(self, transaksi: Transaksi) -> None:
        self._storage.append(transaksi)

    def get_total_pendapatan(self, mulai: datetime, akhir: datetime) -> float:
        # Menjumlahkan total_bayar dari semua transaksi dalam periode
        transaksi_periode = self.get_by_periode(mulai, akhir)
        return sum(t.total_bayar for t in transaksi_periode)


# Section 4: Service (Logic)
# Urutan transisi status yang valid (UC06)
urutan_status = [
    StatusPesanan.menunggu,
    StatusPesanan.diterima,
    StatusPesanan.diproses,
    StatusPesanan.siap_diambil,
    StatusPesanan.selesai,
]

class PesananService:
    # Service untuk logika bisnis UC04 dan UC06
    # Bergantung pada IPesananRepository & ITransaksiRepository (bukan kelas konkret)
    def __init__(self, pesanan_repo: IPesananRepository,
                 transaksi_repo: ITransaksiRepository):
        self._pesanan_repo    = pesanan_repo     
        self._transaksi_repo  = transaksi_repo   
        self._next_trx_id     = 1

    def daftar_pesanan(self) -> List[Pesanan]:
        # Mengambil semua pesanan yang ada (UC04 - Mengelola Daftar Pesanan)
        return self._pesanan_repo.get_all()

    def terima_pesanan(self, id: int) -> str:
        pesanan = self._pesanan_repo.get_by_id(id)
        if not pesanan:
            return f"[ERROR] Pesanan ID {id} tidak ditemukan."
        if pesanan.status != StatusPesanan.menunggu:
            return f"[ERROR] Pesanan tidak dalam status menunggu (status saat ini: {pesanan.status.value})."

        self._pesanan_repo.update_status(id, StatusPesanan.diterima)
        trx = Transaksi(self._next_trx_id, pesanan)
        self._transaksi_repo.add(trx)
        self._next_trx_id += 1
        return f"[OK] Pesanan ID {id} ({pesanan.nama_pelanggan}) diterima. Transaksi #{trx.id} dibuat."

    def tolak_pesanan(self, id: int) -> str:
        """Petugas menolak pesanan → status Ditolak."""
        pesanan = self._pesanan_repo.get_by_id(id)
        if not pesanan:
            return f"[ERROR] Pesanan ID {id} tidak ditemukan."
        if pesanan.status != StatusPesanan.menunggu:
            return f"[ERROR] Hanya pesanan menunggu yang dapat Ditolak."

        self._pesanan_repo.update_status(id, StatusPesanan.Ditolak)
        return f"[OK] Pesanan ID {id} Ditolak."

    def update_status(self, id: int, status_baru: StatusPesanan) -> str:
        pesanan = self._pesanan_repo.get_by_id(id)
        if not pesanan:
            return f"[ERROR] Pesanan ID {id} tidak ditemukan."

        # Validasi urutan status
        if pesanan.status not in urutan_status or status_baru not in urutan_status:
            return f"[ERROR] Transisi status tidak valid."

        idx_saat_ini = urutan_status.index(pesanan.status)
        idx_baru     = urutan_status.index(status_baru)

        if idx_baru != idx_saat_ini + 1:
            return (f"[ERROR] Transisi '{pesanan.status.value}' → '{status_baru.value}' "
                    f"tidak diizinkan. Status harus berurutan.")

        status_lama = pesanan.status.value
        self._pesanan_repo.update_status(id, status_baru)
        return f"[OK] Status pesanan ID {id} diperbarui: {status_lama} → {status_baru.value}"


class LaporanService:
    # Service untuk logika bisnis UC07 dan UC07.1.
    def __init__(self, transaksi_repo: ITransaksiRepository):
        self._transaksi_repo = transaksi_repo   

    def get_laporan(self, mulai: datetime, akhir: datetime) -> dict:
        transaksi = self._transaksi_repo.get_by_periode(mulai, akhir)
        if not transaksi:
            return {"error": "Tidak ada data pada periode ini."}

        # Hitung menu terlaris
        menu_counter: dict = {}
        for t in transaksi:
            for item in t.pesanan.items:
                nama = item.menu.nama
                menu_counter[nama] = menu_counter.get(nama, 0) + item.jumlah

        menu_terlaris = max(menu_counter, key=menu_counter.get) if menu_counter else "-"
        total         = self._transaksi_repo.get_total_pendapatan(mulai, akhir)

        return {
            "periode"        : f"{mulai.strftime('%d/%m/%Y')} – {akhir.strftime('%d/%m/%Y')}",
            "jumlah_transaksi": len(transaksi),
            "total_pendapatan": total,
            "menu_terlaris"  : f"{menu_terlaris} ({menu_counter.get(menu_terlaris, 0)}x)",
            "detail"         : transaksi,
        }

    def export_pdf(self, laporan: dict) -> str:
        if "error" in laporan:
            return "[ERROR] Tidak ada data."
        nama_file = f"laporan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = canvas.Canvas(nama_file)
        y = 800
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(180, y, "Laporan TCanteen")
        y -= 40
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, y, f"Periode : {laporan['periode']}")
        y -= 20
        pdf.drawString(50, y, f"Jumlah Transaksi : {laporan['jumlah_transaksi']}")
        y -= 20
        pdf.drawString(50, y, f"Total Pendapatan : Rp{laporan['total_pendapatan']:,.0f}")
        y -= 20
        pdf.drawString(50, y, f"Menu Terlaris : {laporan['menu_terlaris']}")
        y -= 40
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(50, y, "Detail Transaksi")
        y -= 30
        pdf.setFont("Helvetica", 11)
        for trx in laporan["detail"]:
            pdf.drawString(
                50,
                y,
                f"Transaksi #{trx.id} | {trx.pesanan.nama_pelanggan}"
            )
            y -= 20
            for item in trx.pesanan.items:
                pdf.drawString(
                    70,
                    y,
                    f"{item.menu.nama} "
                    f"x{item.jumlah} "
                    f"= Rp{item.subtotal:,.0f}"
                )
                y -= 20
            pdf.drawString(
                70,
                y,
                f"Total : Rp{trx.total_bayar:,.0f}"
            )
            y -= 30
            if y < 100:
                pdf.showPage()
                y = 800
        pdf.save()

        return f"[OK] PDF berhasil dibuat: {nama_file}"

# Section 5: Controller
class PesananController:

    def __init__(self, service: PesananService):
        self._service = service

    def tampilkan_daftar_pesanan(self):
        print("\n")
        print("  DAFTAR PESANAN MASUK")
        print("-"*60)
        pesanan_list = self._service.daftar_pesanan()
        if not pesanan_list:
            print("  [INFO] Belum ada pesanan.")
        for p in pesanan_list:
            print(f"\n  {p}")
            for item in p.items:
                print(f"  {item}")
            print(f"  Jenis: {p.jenis_penyajian} | Waktu: {p.waktu_pesanan.strftime('%H:%M:%S')}")

    def terima_pesanan(self, id: int):
        result = self._service.terima_pesanan(id)
        print(f"  {result}")

    def tolak_pesanan(self, id: int):
        result = self._service.tolak_pesanan(id)
        print(f"  {result}")

    def update_status(self, id: int, status: StatusPesanan):
        result = self._service.update_status(id, status)
        print(f"  {result}")


class LaporanController:
    def __init__(self, service: LaporanService):
        self._service = service

    def tampilkan_laporan(self, mulai: datetime, akhir: datetime):
        print("\n")
        print("  LAPORAN KEUANGAN KANTIN")
        print("-"*60)
        laporan = self._service.get_laporan(mulai, akhir)
        if "error" in laporan:
            print(f"  [INFO] {laporan['error']}")
            return laporan
        print(f"  Periode         : {laporan['periode']}")
        print(f"  Jumlah Transaksi: {laporan['jumlah_transaksi']}")
        print(f"  Total Pendapatan: Rp{laporan['total_pendapatan']:,.0f}")
        print(f"  Menu Terlaris   : {laporan['menu_terlaris']}")
        return laporan

    def unduh_laporan_pdf(self, laporan: dict):
        result = self._service.export_pdf(laporan)
        print(f"  {result}")

# Section 6: Main
def main():
    print("\n")
    print("TCanteen Repository Pattern Demo")
    print("Sistem Pemesanan Kantin Teknik Informatika ITS")
    print("-"*60)

    # Inisialisasi Repository (bisa diganti implementasi lain tanpa ubah service)
    pesanan_repo   = PesananRepository()
    menu_repo      = MenuRepository()
    transaksi_repo = TransaksiRepository()

    # Inisialisasi Service (Dependency Injection)
    pesanan_service = PesananService(pesanan_repo, transaksi_repo)
    laporan_service = LaporanService(transaksi_repo)

    # Inisialisasi Controller
    pesanan_ctrl = PesananController(pesanan_service)
    laporan_ctrl = LaporanController(laporan_service)

    # Setup: Tambah menu ke repository
    menu_repo.add(Menu(1, "Nasi Goreng Spesial", 15000))
    menu_repo.add(Menu(2, "Ayam Bakar",          18000))
    menu_repo.add(Menu(3, "Es Teh Manis",         5000))
    menu_repo.add(Menu(4, "Mie Goreng",           13000))
    menu_repo.add(Menu(5, "Jus Alpukat",          10000))

    print("\n[MENU TERSEDIA]")
    for m in menu_repo.get_all():
        print(f"  {m}")

    # Setup: Buat pesanan dari pelanggan
    m1 = menu_repo.get_by_id(1)  
    m2 = menu_repo.get_by_id(2)   
    m3 = menu_repo.get_by_id(3)  
    m4 = menu_repo.get_by_id(4)  
    m5 = menu_repo.get_by_id(5)

    p1 = Pesanan(1, "Budi Santoso",  [ItemPesanan(m1, 2), ItemPesanan(m3, 2)], "Dine In")
    p2 = Pesanan(2, "Siti Rahayu",   [ItemPesanan(m2, 1), ItemPesanan(m5, 1)], "Take Away")
    p3 = Pesanan(3, "Agus Prasetyo", [ItemPesanan(m4, 1), ItemPesanan(m3, 1)], "Dine In")

    pesanan_repo.add(p1)
    pesanan_repo.add(p2)
    pesanan_repo.add(p3)

    # Demo UC04: Mengelola Daftar Pesanan
    pesanan_ctrl.tampilkan_daftar_pesanan()

    print("\n[AKSI PETUGAS  UC04]")
    pesanan_ctrl.terima_pesanan(1) 
    pesanan_ctrl.terima_pesanan(2)
    pesanan_ctrl.tolak_pesanan(3)
    pesanan_ctrl.terima_pesanan(3)

    # Demo UC06: Update Status Pesanan
    print("\n[AKSI PETUGAS  UC06: Update Status]")
    pesanan_ctrl.update_status(1, StatusPesanan.diproses)
    pesanan_ctrl.update_status(1, StatusPesanan.siap_diambil)
    pesanan_ctrl.update_status(1, StatusPesanan.selesai)
    pesanan_ctrl.update_status(1, StatusPesanan.diproses)
    pesanan_ctrl.update_status(2, StatusPesanan.selesai)    
    pesanan_ctrl.update_status(2, StatusPesanan.diproses) 
    pesanan_ctrl.update_status(2, StatusPesanan.siap_diambil)
    pesanan_ctrl.update_status(2, StatusPesanan.selesai)

    # Demo UC07: Laporan Keuangan
    print("\n[LAPORAN  UC07 & UC07.1]")
    mulai  = datetime(2024, 1, 1)
    akhir  = datetime(2099, 12, 31)
    laporan = laporan_ctrl.tampilkan_laporan(mulai, akhir)
    laporan_ctrl.unduh_laporan_pdf(laporan)

    # Demo: Status akhir semua pesanan
    pesanan_ctrl.tampilkan_daftar_pesanan()

    print("\n")
    print("Demo selesai.")
    print("-"*60 + "\n")


if __name__ == "__main__":
    main()