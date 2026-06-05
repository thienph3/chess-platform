import AddIcon from "@mui/icons-material/Add";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import Skeleton from "@mui/material/Skeleton";
import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import { DataGrid, GridColDef, GridPaginationModel } from "@mui/x-data-grid";
import { useState } from "react";

import AppSnackbar from "@/components/AppSnackbar";
import { dataGridLocaleText } from "@/utils/dataGridLocale";

import FinanceChart from "../components/FinanceChart";
import TransactionFormDialog from "../components/TransactionFormDialog";
import { useBalance } from "../hooks/useBalance";
import { useCreateTransaction, useUpdateTransaction } from "../hooks/useTransactionMutations";
import { useTransactions } from "../hooks/useTransactions";
import { ITransaction, ITransactionCreate, TransactionType } from "../types";

const TYPE_LABELS: Record<TransactionType, string> = { income: "Thu", expense: "Chi" };
const CATEGORY_LABELS: Record<string, string> = {
  membership_fee: "Phí thành viên", sponsorship: "Tài trợ", donation: "Quyên góp", other_income: "Thu khác",
  venue: "Địa điểm", prize: "Giải thưởng", equipment: "Thiết bị", food: "Ăn uống", other_expense: "Chi khác",
};

function formatCurrency(value: number): string {
  return `${value.toLocaleString("vi-VN")} ₫`;
}

const columns: GridColDef[] = [
  { field: "date", headerName: "Ngày", width: 120 },
  { field: "type", headerName: "Loại", width: 80, valueGetter: (value: TransactionType) => TYPE_LABELS[value] || value },
  { field: "category", headerName: "Danh mục", width: 140, valueGetter: (value: string) => CATEGORY_LABELS[value] || value },
  { field: "amount", headerName: "Số tiền", width: 140, valueFormatter: (value: number) => formatCurrency(value) },
  { field: "description", headerName: "Mô tả", flex: 1 },
];

function FinancePage() {
  const [activeTab, setActiveTab] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [type, setType] = useState<TransactionType | "">("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editTx, setEditTx] = useState<ITransaction | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({
    open: false, message: "", severity: "success",
  });

  const { data: balanceData, isLoading: balanceLoading } = useBalance();
  const { data: txData, isLoading: txLoading } = useTransactions({ page: page + 1, pageSize, type });
  const createMutation = useCreateTransaction();
  const updateMutation = useUpdateTransaction();

  const handleCreate = () => { setEditTx(null); setDialogOpen(true); };
  const handleEdit = (tx: ITransaction) => { setEditTx(tx); setDialogOpen(true); };

  const handleSubmit = async (formData: ITransactionCreate) => {
    try {
      if (editTx) {
        await updateMutation.mutateAsync({ id: editTx.id, data: formData });
        setSnackbar({ open: true, message: "Cập nhật giao dịch thành công", severity: "success" });
      } else {
        await createMutation.mutateAsync(formData);
        setSnackbar({ open: true, message: "Thêm giao dịch thành công", severity: "success" });
      }
      setDialogOpen(false);
    } catch {
      setSnackbar({ open: true, message: "Có lỗi xảy ra", severity: "error" });
    }
  };

  if (balanceLoading || txLoading) {
    return <Box p={3}><Skeleton variant="rectangular" height={400} /></Box>;
  }

  const balance = balanceData?.data;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>Tài chính</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreate}>Thêm giao dịch</Button>
      </Stack>
      <Stack direction="row" spacing={2} mb={3}>
        <BalanceCard title="Tổng thu" value={balance?.total_income || 0} color="success.main" />
        <BalanceCard title="Tổng chi" value={balance?.total_expense || 0} color="error.main" />
        <BalanceCard title="Số dư" value={balance?.balance || 0} color="primary.main" />
      </Stack>
      <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 2 }}>
        <Tab label="Giao dịch" />
        <Tab label="Báo cáo" />
      </Tabs>
      {activeTab === 0 && (
        <>
          <Stack direction="row" spacing={2} mb={2}>
            <FormControl size="small" sx={{ minWidth: 140 }}>
              <InputLabel>Loại</InputLabel>
              <Select value={type} label="Loại" onChange={(e: SelectChangeEvent) => setType(e.target.value as TransactionType | "")}>
                <MenuItem value="">Tất cả</MenuItem>
                <MenuItem value="income">Thu</MenuItem>
                <MenuItem value="expense">Chi</MenuItem>
              </Select>
            </FormControl>
          </Stack>
          <DataGrid
            rows={txData?.data || []}
            columns={columns}
            rowCount={txData?.total || 0}
            paginationMode="server"
            paginationModel={{ page, pageSize }}
            onPaginationModelChange={(model: GridPaginationModel) => { setPage(model.page); setPageSize(model.pageSize); }}
            onRowClick={(params) => handleEdit(params.row as ITransaction)}
            pageSizeOptions={[10, 20, 50]}
            disableRowSelectionOnClick
            autoHeight
            localeText={dataGridLocaleText}
          />
        </>
      )}
      {activeTab === 1 && <FinanceChart />}
      <TransactionFormDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSubmit={handleSubmit}
        transaction={editTx}
        isLoading={createMutation.isPending || updateMutation.isPending}
      />
      <AppSnackbar
        open={snackbar.open}
        message={snackbar.message}
        severity={snackbar.severity}
        onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
      />
    </Box>
  );
}

interface BalanceCardProps { title: string; value: number; color: string; }

function BalanceCard({ title, value, color }: BalanceCardProps) {
  return (
    <Card sx={{ flex: 1 }}>
      <CardContent>
        <Typography variant="body2" color="text.secondary">{title}</Typography>
        <Typography variant="h6" fontWeight={600} color={color}>{formatCurrency(value)}</Typography>
      </CardContent>
    </Card>
  );
}

export default FinancePage;
