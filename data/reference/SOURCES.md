# Reference data sources

| File | What it is | Source | Retrieved |
|---|---|---|---|
| `mercado_continuo_2026-10-23.csv` | Every stock on BME's main market (Mercado Continuo), with trading status. `yahoo_symbol` and `domicile` were added by hand. | [BME Exchange, Mercado Continuo prices page](https://www.bolsasymercados.es/es/bme-exchange/mercados-y-cotizaciones/acciones/mercado-continuo.html), session of 23 Oct 2026 | 25 Oct 2026 |
| `ftt_list_2026.csv` | Spanish companies with market cap above €1bn on 1 Dec 2025. Purchases of these shares pay the 0.2% financial transaction tax during 2026. `yahoo_symbol` was added by hand (blank = not traded on the Mercado Continuo). | [Agencia Tributaria, RELACION_SOCIEDADES_EJERCICIO_2026.pdf](https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/Declaraciones_informativas/I_Transacciones_Financieras/RELACION_SOCIEDADES_EJERCICIO_2026.pdf) | 25 Oct 2026 |

## Other inputs used in `src/costs.py`

| Input | Value used | Source | Retrieved |
|---|---|---|---|
| Transaction-tax lists, 2021–2025 | None of the 10 stocks appears on any list (52–59 companies per year) | Agencia Tributaria: [2021](https://sede.agenciatributaria.gob.es/static_files/Sede/Procedimiento_ayuda/GC44/castellano/Relacion_Sociedades_web.pdf), [2022](https://sede.agenciatributaria.gob.es/static_files/Sede/Procedimiento_ayuda/GC44/castellano/Relacion_Sociedades_web01_12_21.pdf), [2023](https://sede.agenciatributaria.gob.es/static_files/Sede/Procedimiento_ayuda/GC44/castellano/Relacion_Sociedades_web-01-12-22.pdf), [2024](https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/Declaraciones_informativas/I_Transacciones_Financieras/RELACION_SOCIEDADES_EJER_2024.pdf), [2025](https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/Declaraciones_informativas/I_Transacciones_Financieras/RELACION_SOCIEDADES_EJER_2025.pdf) | 25 Oct 2026 |
| Commission | 0.05% per order, €3 minimum (Interactive Brokers fixed pricing, Spain) | [Rankia review of Interactive Brokers](https://www.rankia.com/blog/mejores-brokers/4652044-analisis-interactive-brokers-regulacion-mercados-comisiones-mucho-mas?page=2). Third-party: IBKR's own pricing page blocked automated access, so check it directly. | 25 Oct 2026 |
| Bid-ask spread estimator | EDGE, via the authors' `bidask` package (v2.1.0) | Ardia, Guidotti & Kroencke (2024), [Journal of Financial Economics 161, 103916](https://doi.org/10.1016/j.jfineco.2024.103916) | 25 Oct 2026 |
| Spread estimator (compared, not used) | Abdi-Ranaldo | Abdi & Ranaldo (2017), [Review of Financial Studies 30(12)](https://doi.org/10.1093/rfs/hhx084) | 25 Oct 2026 |
| Cash rate (notebook 05) | ECB deposit facility rate, daily, cached in `data/raw/ecb_deposit_rate.csv` | [ECB Data Portal, series FM.D.U2.EUR.4F.KR.DFR.LEV](https://data.ecb.europa.eu/data/datasets/FM/FM.D.U2.EUR.4F.KR.DFR.LEV) | 25 Oct 2026 |
