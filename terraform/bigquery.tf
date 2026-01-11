resource "google_bigquery_dataset" "meu_dataset" {
  dataset_id                  = "teste_alex"
  friendly_name               = "Dataset de Vendas"
  description                 = "Armazena tabelas de transações comerciais"
  location                    = "southamerica-east1"
  delete_contents_on_destroy  = false # Segurança contra deleção acidental
}

# Criação da Tabela com Schema Inline
resource "google_bigquery_table" "minha_tabela" {
  dataset_id = google_bigquery_dataset.meu_dataset.dataset_id
  table_id   = "teste_resultados"
  deletion_protection = false # Altere para true em produção

#   schema = <<EOF
# [
#   {
#     "name": "id_transacao",
#     "type": "STRING",
#     "mode": "REQUIRED",
#     "description": "ID único da venda"
#   },
#   {
#     "name": "data_venda",
#     "type": "DATE",
#     "mode": "NULLABLE"
#   },
#   {
#     "name": "valor",
#     "type": "FLOAT",
#     "mode": "NULLABLE"
#   }
# ]
# EOF
}