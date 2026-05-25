# TCanteen: Sistem Pemesanan Kantin Teknik Informatika ITS
# Repository Pattern (Python)
#  PPL D11

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from enum import Enum
from reportlab.pdfgen import canvas


# Model Entity

class StatusPesanan(Enum):
    menunggu     = "menunggu"
    diterima     = "diterima"
    diproses     = "diproses"
    siap_diambil = "Siap Diambil"
    selesai      = "selesai"
    Ditolak      = "Ditolak"

urutan_status = [
    StatusPesanan.menunggu, StatusPesanan.diterima,
    StatusPesanan.diproses, StatusPesanan.siap_diambil, StatusPesanan.selesai,
]

class Menu:
    def __init__(self, id: int, nama: str, harga: float, tersedia: bool = True):
        self.id, self.nama, self.harga, self.tersedia = id, nama, harga, tersedia

    def __repr__(self):
        return f"Menu({self.id}, '{self.nama}', Rp{self.harga:,.0f}, {'Tersedia' if self.tersedia else 'Habis'})"

class ItemPesanan:
    def __init__(self, menu: Menu, jumlah: int):
        self.menu, self.jumlah = menu, jumlah

    @property
    def subtotal(self): return self.menu.harga * self.jumlah

    def __repr__(self):
        return f"  - {self.menu.nama} x{self.jumlah} = Rp{self.subtotal:,.0f}"

class Pesanan:
    def __init__(self, id: int, nama_pelanggan: str, items: List[ItemPesanan], jenis_penyajian: str = "Dine In"):
        self.id, self.nama_pelanggan, self.items, self.jenis_penyajian = id, nama_pelanggan, items, jenis_penyajian
        self.status        = StatusPesanan.menunggu
        self.waktu_pesanan = datetime.now()

    @property
    def total_harga(self): return sum(i.subtotal for i in self.items)

    def __repr__(self):
        return f"Pesanan({self.id}, '{self.nama_pelanggan}', Rp{self.total_harga:,.0f}, {self.status.value})"

class Transaksi:
    def __init__(self, id: int, pesanan: Pesanan, tanggal: datetime = None):
        self.id, self.pesanan     = id, pesanan
        self.total_bayar          = pesanan.total_harga
        self.tanggal              = tanggal or datetime.now()

    def __repr__(self):
        return f"Transaksi({self.id}, pesanan={self.pesanan.id}, Rp{self.total_bayar:,.0f}, {self.tanggal:%Y-%m-%d})"


# Interfaces Repository

class IPesananRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Pesanan]: pass
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Pesanan]: pass
    @abstractmethod
    def add(self, pesanan: Pesanan) -> None: pass
    @abstractmethod
    def update_status(self, id: int, status: StatusPesanan) -> bool: pass
    @abstractmethod
    def delete(self, id: int) -> bool: pass

class IMenuRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Menu]: pass
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Menu]: pass
    @abstractmethod
    def add(self, menu: Menu) -> None: pass
    @abstractmethod
    def update(self, menu: Menu) -> bool: pass
    @abstractmethod
    def delete(self, id: int) -> bool: pass

class ITransaksiRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Transaksi]: pass
    @abstractmethod
    def get_by_periode(self, mulai: datetime, akhir: datetime) -> List[Transaksi]: pass
    @abstractmethod
    def add(self, transaksi: Transaksi) -> None: pass
    @abstractmethod
    def get_total_pendapatan(self, mulai: datetime, akhir: datetime) -> float: pass


# In Memory Repository

class _BaseRepo:
    def __init__(self): self._storage = []
    def get_all(self): return list(self._storage)
    def _find(self, id): return next((x for x in self._storage if x.id == id), None)
    def _remove(self, id):
        obj = self._find(id)
        if obj: self._storage.remove(obj); return True
        return False

class PesananRepository(_BaseRepo, IPesananRepository):
    def get_by_id(self, id): return self._find(id)
    def add(self, pesanan): self._storage.append(pesanan)
    def update_status(self, id, status):
        p = self._find(id)
        if p: p.status = status; return True
        return False
    def delete(self, id): return self._remove(id)

class MenuRepository(_BaseRepo, IMenuRepository):
    def get_by_id(self, id): return self._find(id)
    def add(self, menu): self._storage.append(menu)
    def update(self, menu):
        e = self._find(menu.id)
        if e: e.nama, e.harga, e.tersedia = menu.nama, menu.harga, menu.tersedia; return True
        return False
    def delete(self, id): return self._remove(id)

class TransaksiRepository(_BaseRepo, ITransaksiRepository):
    def get_by_id(self, id): return self._find(id)
    def add(self, transaksi): self._storage.append(transaksi)
    def get_by_periode(self, mulai, akhir):
        return [t for t in self._storage if mulai <= t.tanggal <= akhir]
    def get_total_pendapatan(self, mulai, akhir):
        return sum(t.total_bayar for t in self.get_by_periode(mulai, akhir))


# Services

class PesananService:
    def __init__(self, pesanan_repo: IPesananRepository, transaksi_repo: ITransaksiRepository):
        self._pr, self._tr, self._next_trx_id = pesanan_repo, transaksi_repo, 1

    def daftar_pesanan(self): return self._pr.get_all()

    def terima_pesanan(self, id: int) -> str:
        p = self._pr.get_by_id(id)
        if not p: return f"[ERROR] Pesanan ID {id} tidak ditemukan."
        if p.status != StatusPesanan.menunggu:
            return f"[ERROR] Status bukan menunggu (saat ini: {p.status.value})."
        self._pr.update_status(id, StatusPesanan.diterima)
        trx = Transaksi(self._next_trx_id, p); self._tr.add(trx); self._next_trx_id += 1
        return f"[OK] Pesanan ID {id} ({p.nama_pelanggan}) diterima. Transaksi #{trx.id} dibuat."

    def tolak_pesanan(self, id: int) -> str:
        p = self._pr.get_by_id(id)
        if not p: return f"[ERROR] Pesanan ID {id} tidak ditemukan."
        if p.status != StatusPesanan.menunggu: return "[ERROR] Hanya pesanan menunggu yang dapat Ditolak."
        self._pr.update_status(id, StatusPesanan.Ditolak)
        return f"[OK] Pesanan ID {id} Ditolak."

    def update_status(self, id: int, status_baru: StatusPesanan) -> str:
        p = self._pr.get_by_id(id)
        if not p: return f"[ERROR] Pesanan ID {id} tidak ditemukan."
        if p.status not in urutan_status or status_baru not in urutan_status:
            return "[ERROR] Transisi status tidak valid."
        if urutan_status.index(status_baru) != urutan_status.index(p.status) + 1:
            return f"[ERROR] '{p.status.value}' → '{status_baru.value}' tidak diizinkan."
        lama = p.status.value; self._pr.update_status(id, status_baru)
        return f"[OK] Status pesanan ID {id}: {lama} → {status_baru.value}"


class LaporanService:
    def __init__(self, transaksi_repo: ITransaksiRepository):
        self._tr = transaksi_repo

    def get_laporan(self, mulai: datetime, akhir: datetime) -> dict:
        data = self._tr.get_by_periode(mulai, akhir)
        if not data: return {"error": "Tidak ada data pada periode ini."}
        counter = {}
        for t in data:
            for item in t.pesanan.items:
                counter[item.menu.nama] = counter.get(item.menu.nama, 0) + item.jumlah
        terlaris = max(counter, key=counter.get) if counter else "-"
        return {
            "periode"         : f"{mulai:%d/%m/%Y} – {akhir:%d/%m/%Y}",
            "jumlah_transaksi": len(data),
            "total_pendapatan": self._tr.get_total_pendapatan(mulai, akhir),
            "menu_terlaris"   : f"{terlaris} ({counter.get(terlaris, 0)}x)",
            "detail"          : data,
        }

    def export_pdf(self, laporan: dict) -> str:
        if "error" in laporan: return "[ERROR] Tidak ada data."
        nama_file = f"laporan_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        pdf = canvas.Canvas(nama_file); y = 800
        pdf.setFont("Helvetica-Bold", 16); pdf.drawString(180, y, "Laporan TCanteen"); y -= 40
        pdf.setFont("Helvetica", 12)
        for label, key in [("Periode", "periode"), ("Jumlah Transaksi", "jumlah_transaksi"),
                            ("Total Pendapatan", "total_pendapatan"), ("Menu Terlaris", "menu_terlaris")]:
            val = f"Rp{laporan[key]:,.0f}" if key == "total_pendapatan" else laporan[key]
            pdf.drawString(50, y, f"{label} : {val}"); y -= 20
        y -= 20; pdf.setFont("Helvetica-Bold", 13); pdf.drawString(50, y, "Detail Transaksi"); y -= 30
        pdf.setFont("Helvetica", 11)
        for trx in laporan["detail"]:
            pdf.drawString(50, y, f"Transaksi #{trx.id} | {trx.pesanan.nama_pelanggan}"); y -= 20
            for item in trx.pesanan.items:
                pdf.drawString(70, y, f"{item.menu.nama} x{item.jumlah} = Rp{item.subtotal:,.0f}"); y -= 20
            pdf.drawString(70, y, f"Total : Rp{trx.total_bayar:,.0f}"); y -= 30
            if y < 100: pdf.showPage(); y = 800
        pdf.save()
        return f"[OK] PDF berhasil dibuat: {nama_file}"


# Controllers

class PesananController:
    def __init__(self, service: PesananService): self._s = service

    def tampilkan_daftar_pesanan(self):
        print("\n  DAFTAR PESANAN MASUK\n" + "-"*60)
        data = self._s.daftar_pesanan()
        if not data: print("  [INFO] Belum ada pesanan."); return
        for p in data:
            print(f"\n  {p}")
            for item in p.items: print(f"  {item}")
            print(f"  Jenis: {p.jenis_penyajian} | Waktu: {p.waktu_pesanan:%H:%M:%S}")

    def terima_pesanan(self, id): print(f"  {self._s.terima_pesanan(id)}")
    def tolak_pesanan(self, id):  print(f"  {self._s.tolak_pesanan(id)}")
    def update_status(self, id, status): print(f"  {self._s.update_status(id, status)}")


class LaporanController:
    def __init__(self, service: LaporanService): self._s = service

    def tampilkan_laporan(self, mulai: datetime, akhir: datetime) -> dict:
        print("\n  LAPORAN KEUANGAN KANTIN\n" + "-"*60)
        lap = self._s.get_laporan(mulai, akhir)
        if "error" in lap: print(f"  [INFO] {lap['error']}"); return lap
        print(f"  Periode         : {lap['periode']}")
        print(f"  Jumlah Transaksi: {lap['jumlah_transaksi']}")
        print(f"  Total Pendapatan: Rp{lap['total_pendapatan']:,.0f}")
        print(f"  Menu Terlaris   : {lap['menu_terlaris']}")
        return lap

    def unduh_laporan_pdf(self, laporan): print(f"  {self._s.export_pdf(laporan)}")


# Main Program

def main():
    print("\nTCanteen Repository Pattern Demo\nSistem Pemesanan Kantin TI ITS\n" + "-"*60)

    pesanan_repo   = PesananRepository()
    menu_repo      = MenuRepository()
    transaksi_repo = TransaksiRepository()

    pesanan_ctrl = PesananController(PesananService(pesanan_repo, transaksi_repo))
    laporan_ctrl = LaporanController(LaporanService(transaksi_repo))

    for args in [(1,"Nasi Goreng Spesial",15000),(2,"Ayam Bakar",18000),(3,"Es Teh Manis",5000),
                 (4,"Mie Goreng",13000),(5,"Jus Alpukat",10000)]:
        menu_repo.add(Menu(*args))

    print("\n[MENU TERSEDIA]")
    for m in menu_repo.get_all(): print(f"  {m}")

    g = menu_repo.get_by_id
    pesanan_repo.add(Pesanan(1, "Budi Santoso",  [ItemPesanan(g(1), 2), ItemPesanan(g(3), 2)], "Dine In"))
    pesanan_repo.add(Pesanan(2, "Siti Rahayu",   [ItemPesanan(g(2), 1), ItemPesanan(g(5), 1)], "Take Away"))
    pesanan_repo.add(Pesanan(3, "Agus Prasetyo", [ItemPesanan(g(4), 1), ItemPesanan(g(3), 1)], "Dine In"))

    pesanan_ctrl.tampilkan_daftar_pesanan()

    print("\n[AKSI PETUGAS — UC04]")
    pesanan_ctrl.terima_pesanan(1); pesanan_ctrl.terima_pesanan(2)
    pesanan_ctrl.tolak_pesanan(3);  pesanan_ctrl.terima_pesanan(3)

    print("\n[AKSI PETUGAS — UC06: Update Status]")
    S = StatusPesanan
    for id, st in [(1,S.diproses),(1,S.siap_diambil),(1,S.selesai),(1,S.diproses),
                   (2,S.selesai),(2,S.diproses),(2,S.siap_diambil),(2,S.selesai)]:
        pesanan_ctrl.update_status(id, st)

    print("\n[LAPORAN — UC07 & UC07.1]")
    lap = laporan_ctrl.tampilkan_laporan(datetime(2024,1,1), datetime(2099,12,31))
    laporan_ctrl.unduh_laporan_pdf(lap)

    pesanan_ctrl.tampilkan_daftar_pesanan()
    print("\nDemo selesai.\n" + "-"*60)


if __name__ == "__main__":
    main()