/** 폼 제출 실패 Alert — 입력 시 에러만 제거 (성공 메시지는 유지) */

export type FormErrorState = {
  formError: string | null
}

export function formErrorClearPatch(): FormErrorState {
  return { formError: null }
}

export function mergeFieldAndClearFormError<K extends string, V>(
  field: K,
  value: V,
): FormErrorState & Record<K, V> {
  return { [field]: value, formError: null } as FormErrorState & Record<K, V>
}
