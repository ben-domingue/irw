# Audit diff: chile_2023_social-welfare-survey_h

Classification (suggested): **review**

## Summary

- item coverage: OK (missed=0, extra=0)
- resp-set alignment rate: 0.9231
- mean item_text similarity: 0.5164
- mean option_text similarity: 0.8957
- mean context (instructions/section_prompt) similarity: n/a
- instructions/section_prompt swaps detected: 0

## Itemized mismatches

- `h1` -- option_text_presence_mismatch (resp=3)
- `h1` -- option_text_presence_mismatch (resp=2)
- `h2_a` -- option_text_presence_mismatch (resp=1)
- `h2_a` -- option_text_presence_mismatch (resp=3)
- `h2_a` -- option_text_presence_mismatch (resp=2)
- `h2_a` -- option_text_presence_mismatch (resp=4)
- `h2_a` -- option_text_presence_mismatch (resp=5)
- `h2_b` -- option_text_presence_mismatch (resp=1)
- `h2_b` -- option_text_presence_mismatch (resp=2)
- `h2_b` -- option_text_presence_mismatch (resp=3)
- `h2_b` -- option_text_presence_mismatch (resp=4)
- `h2_c` -- option_text_presence_mismatch (resp=4)
- `h2_c` -- option_text_presence_mismatch (resp=3)
- `h2_d` -- option_text_presence_mismatch (resp=1)
- `h2_d` -- option_text_presence_mismatch (resp=2)
- `h2_d` -- option_text_presence_mismatch (resp=4)
- `h3_a` -- option_text_presence_mismatch (resp=1)
- `h3_b` -- option_text_presence_mismatch (resp=1)
- `h3_b` -- option_text_presence_mismatch (resp=2)
- `h3_c` -- option_text_mismatch (resp=1)
- `h3_d` -- option_text_mismatch (resp=1)
- `h3_e` -- resp_set_mismatch (curated={1,2} fresh={1,2,3})
- `h3_e` -- option_text_presence_mismatch (resp=2)
- `h3_e` -- option_text_presence_mismatch (resp=1)
- `h4_a` -- option_text_mismatch (resp=1)
- `h4_a` -- option_text_presence_mismatch (resp=2)
- `h4_b` -- option_text_presence_mismatch (resp=1)
- `h4_b` -- option_text_presence_mismatch (resp=2)
- `h4_c` -- option_text_presence_mismatch (resp=1)
- `h1` -- item_text_mismatch
- `h2_b` -- item_text_mismatch
- `h3_a` -- item_text_mismatch
- `h3_b` -- item_text_mismatch
- `h3_c` -- item_text_mismatch
- `h3_d` -- item_text_mismatch
- `h3_e` -- item_text_mismatch
- `h4_a` -- item_text_mismatch
- `h4_b` -- item_text_mismatch
- `h4_c` -- item_text_mismatch

## Field-level values for mismatched items

### `h3_c` / option_text[resp=1] (similarity 0.5)
- curated: `Sí`
- fresh: `Si`

### `h3_d` / option_text[resp=3] (similarity 0.9348)
- curated: `No hay niños niñas o adolescentes en el hogar`
- fresh: `No hay ninos, ninas o adolescentes en el hogar`

### `h3_d` / option_text[resp=1] (similarity 0.5)
- curated: `Sí`
- fresh: `Si`

### `h4_a` / option_text[resp=1] (similarity 0.5)
- curated: `Sí`
- fresh: `Si`

### `h1` / item_text (similarity 0.5124)
- curated: `¿Cuántas veces ha sido víctima de un delito, como asalto o robo?`
- fresh: `En los ultimos 12 meses, ¿cuantas veces ha sido victima de un delito, como asalto o robo al interior o fuera de su hogar?`

### `h2_a` / item_text (similarity 0.6486)
- curated: `Cuánta seguridad tiene: Cuando está en plazas,parques o espacios naturales`
- fresh: `Cuando esta en plazas, parques o espacios naturales`

### `h2_b` / item_text (similarity 0.5902)
- curated: `Cuánta seguridad tiene: Caminando de día por calles o caminos`
- fresh: `Caminando de dia por calles o caminos`

### `h2_c` / item_text (similarity 0.619)
- curated: `Cuánta seguridad tiene: Caminando de noche por calles o caminos`
- fresh: `Caminando de noche por calles o caminos`

### `h2_d` / item_text (similarity 0.6212)
- curated: `Cuánta seguridad tiene: Cuando está dentro de su vivienda o predio`
- fresh: `Cuando esta dentro de su vivienda o predio`

### `h3_a` / item_text (similarity 0.4762)
- curated: `Por temor a delito: ¿Dejó de salir de día?`
- fresh: `¿Dejo de salir de dia?`

### `h3_b` / item_text (similarity 0.5227)
- curated: `Por temor a delito: ¿Dejó de salir de noche?`
- fresh: `¿Dejo de salir de noche?`

### `h3_c` / item_text (similarity 0.5556)
- curated: `Por temor a delito: ¿Dejó de llevar dinero, joyas, documentos o celular?`
- fresh: `¿Dejo de llevar dinero en efectivo, joyas, documentos o celular?`

### `h3_d` / item_text (similarity 0.3978)
- curated: `Por temor a delito:¿dejó de permitir salir a NNA que salgan por su cuenta?`
- fresh: `¿Dejo de permitir que ninas, ninos o adolescentes que viven en su hogar salgan por su cuenta?`

### `h3_e` / item_text (similarity 0.5849)
- curated: `Por temor a delito: ¿Dejó de usar transporte público?`
- fresh: `¿Dejo de usar transporte publico?`

### `h4_a` / item_text (similarity 0.2308)
- curated: `En su barrio tiene: Vigilancia policial de carabineros`
- fresh: `Vigilancia policial de carabineros como plan cuadrante, fiscalizaciones, rondas, presencia.`

### `h4_b` / item_text (similarity 0.5714)
- curated: `En su barrio tiene: Seguridad ciudadana municipal`
- fresh: `Seguridad ciudadana municipal.`

### `h4_c` / item_text (similarity 0.3827)
- curated: `En su barrio tiene: Instancias de org. vecinal (grupo de WhatsApp o alarmas)`
- fresh: `Instancias de organizacion vecinal como grupos de WhatsApp, alarmas comunitarias.`

