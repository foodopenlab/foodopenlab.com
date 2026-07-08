"use client"

import { useEffect, useState } from "react"
import { useMyPageAuth } from "@/hooks/use-mypage-auth"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"
import { Spinner } from "@/components/ui/spinner"
import { Newspaper, Utensils, Check, AlertTriangle, HelpCircle, Save, ArrowRight } from "lucide-react"
import { cn } from "@/lib/utils"

interface Category {
  code: string
  type: "media" | "foodtype"
  parent_code: string | null
  depth: number
  is_flat: boolean
  name_ko: string
  keywords: string[]
}

interface FoodtypeSelectionItem {
  code: string
  parent_code: string | null
}

export default function IndustrySettingsPage() {
  const { token, role, isLoading: isAuthLoading } = useMyPageAuth()
  
  // Data State
  const [categories, setCategories] = useState<Category[]>([])
  const [activeTab, setActiveTab] = useState<"media" | "foodtype">("media")
  
  // Selection State
  const [selectedMedia, setSelectedMedia] = useState<string[]>([])
  const [selectedFoodParents, setSelectedFoodParents] = useState<string[]>([]) // Max 3
  const [selectedFoodChildren, setSelectedFoodChildren] = useState<Record<string, string[]>>({}) // parentCode -> childCodes[] (Max 3 each)

  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const { toast } = useToast()

  // Load categories and current selections
  useEffect(() => {
    if (isAuthLoading || !token) return
    if (role !== "expert") {
      setIsLoading(false)
      return
    }

    async function loadData() {
      try {
        setIsLoading(true)
        
        // 1. Fetch categories
        const catRes = await fetch("/api/admin/industry-categories")
        if (!catRes.ok) throw new Error("카테고리 정보를 불러오지 못했습니다.")
        const catData: Category[] = await catRes.json()
        setCategories(catData)

        // 2. Fetch current selections
        const myRes = await fetch("/api/mypage/industry", {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!myRes.ok) throw new Error("내 설정 정보를 불러오지 못했습니다.")
        const myData = await myRes.json()
        
        setSelectedMedia(myData.media_codes || [])

        // Map selections
        const initialParents: string[] = []
        const initialChildren: Record<string, string[]> = {}
        
        const catMap = new Map(catData.map(c => [c.code, c]))

        const foodSelections: FoodtypeSelectionItem[] = myData.foodtype_selections || []
        foodSelections.forEach(item => {
          const cat = catMap.get(item.code)
          if (cat) {
            if (cat.is_flat) {
              // Flat parent
              if (!initialParents.includes(cat.code)) {
                initialParents.push(cat.code)
              }
            } else if (cat.depth === 2 && cat.parent_code) {
              // Standard child category
              const parentCode = cat.parent_code
              if (!initialParents.includes(parentCode)) {
                initialParents.push(parentCode)
              }
              if (!initialChildren[parentCode]) {
                initialChildren[parentCode] = []
              }
              initialChildren[parentCode].push(cat.code)
            }
          }
        })

        setSelectedFoodParents(initialParents)
        setSelectedFoodChildren(initialChildren)

      } catch (err: any) {
        toast({
          variant: "destructive",
          title: "데이터 로드 실패",
          description: err.message || "오류가 발생했습니다."
        })
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [token, isAuthLoading, role, toast])

  // Split categories for easier rendering
  const mediaCategories = categories.filter(c => c.type === "media" && c.depth === 1)
  const foodtypeParents = categories.filter(c => c.type === "foodtype" && c.depth === 1)
  const foodtypeChildren = categories.filter(c => c.type === "foodtype" && c.depth === 2)

  // Media Source Handler
  const handleMediaToggle = (code: string) => {
    setSelectedMedia(prev => {
      if (prev.includes(code)) {
        return prev.filter(c => c !== code)
      }
      if (prev.length >= 3) {
        toast({
          variant: "destructive",
          title: "선택 제한 초과",
          description: "뉴스 소스는 최대 3개까지 선택 가능합니다."
        })
        return prev
      }
      return [...prev, code]
    })
  }

  // Foodtype Parent Toggle Handler
  const handleFoodParentToggle = (parent: Category) => {
    const code = parent.code
    
    if (selectedFoodParents.includes(code)) {
      // Deselect parent
      setSelectedFoodParents(prev => prev.filter(c => c !== code))
      setSelectedFoodChildren(prev => {
        const copy = { ...prev }
        delete copy[code]
        return copy
      })
    } else {
      // Select parent (Check limit)
      if (selectedFoodParents.length >= 3) {
        toast({
          variant: "destructive",
          title: "선택 제한 초과",
          description: "식품유형 대분류는 최대 3개까지 선택 가능합니다."
        })
        return
      }
      
      setSelectedFoodParents(prev => [...prev, code])
      
      // If parent is flat, no children needed.
      // If parent is standard, initialize children array
      if (!parent.is_flat) {
        setSelectedFoodChildren(prev => ({ ...prev, [code]: [] }))
      }
    }
  }

  // Foodtype Child Selection Handler
  const handleFoodChildToggle = (parentCode: string, childCode: string) => {
    setSelectedFoodChildren(prev => {
      const current = prev[parentCode] || []
      
      if (current.includes(childCode)) {
        return {
          ...prev,
          [parentCode]: current.filter(c => c !== childCode)
        }
      }
      
      if (current.length >= 3) {
        toast({
          variant: "destructive",
          title: "선택 제한 초과",
          description: "대분류당 중분류는 최대 3개까지 선택 가능합니다."
        })
        return prev
      }
      
      return {
        ...prev,
        [parentCode]: [...current, childCode]
      }
    })
  }

  const handleMediaNext = () => {
    if (selectedMedia.length === 0) {
      toast({
        variant: "destructive",
        title: "뉴스 소스를 선택해 주세요",
        description: "최소 1개 이상의 뉴스 소스를 선택한 뒤 다음 단계로 이동할 수 있습니다.",
      })
      return
    }
    setActiveTab("foodtype")
  }

  const handleFoodtypeTabClick = () => {
    if (selectedMedia.length === 0) {
      toast({
        variant: "destructive",
        title: "뉴스 소스를 먼저 선택해 주세요",
        description: "뉴스 소스를 1개 이상 선택한 뒤 식품 유형 단계로 이동할 수 있습니다.",
      })
      return
    }
    setActiveTab("foodtype")
  }

  // Save Config (식품 유형 단계에서만 호출)
  const handleSave = async () => {
    if (selectedMedia.length === 0) {
      toast({
        variant: "destructive",
        title: "설정 저장 실패",
        description: "뉴스 소스 단계에서 최소 1개 이상 선택해 주세요.",
      })
      setActiveTab("media")
      return
    }

    // Validate Food Types
    if (selectedFoodParents.length === 0) {
      toast({
        variant: "destructive",
        title: "설정 저장 실패",
        description: "최소 1개 이상의 식품유형 대분류를 선택해 주세요."
      })
      return
    }

    // Check if any non-flat parent has zero child selections
    for (const parentCode of selectedFoodParents) {
      const parentObj = categories.find(c => c.code === parentCode)
      if (parentObj && !parentObj.is_flat) {
        const children = selectedFoodChildren[parentCode] || []
        if (children.length === 0) {
          toast({
            variant: "destructive",
            title: "설정 저장 실패",
            description: `'${parentObj.name_ko}' 대분류 아래의 중분류를 최소 1개 선택해 주세요.`
          })
          return
        }
      }
    }

    setIsSaving(true)
    try {
      // Assemble foodtype selections
      const foodtypeSelections: FoodtypeSelectionItem[] = []
      
      selectedFoodParents.forEach(parentCode => {
        const parentObj = categories.find(c => c.code === parentCode)
        if (parentObj) {
          if (parentObj.is_flat) {
            foodtypeSelections.push({
              code: parentCode,
              parent_code: null
            })
          } else {
            const children = selectedFoodChildren[parentCode] || []
            children.forEach(childCode => {
              foodtypeSelections.push({
                code: childCode,
                parent_code: parentCode
              })
            })
          }
        }
      })

      const res = await fetch("/api/mypage/industry", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          media_codes: selectedMedia,
          foodtype_selections: foodtypeSelections
        })
      })

      if (!res.ok) {
        const data = await res.json().catch(() => null)
        throw new Error(data?.detail || "업종 설정 저장 실패")
      }

      toast({
        title: "업종 설정 저장 완료",
        description: "변경된 설정에 맞추어 내일 아침 10:30부터 리포트가 새롭게 생성됩니다.",
      })
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "저장 오류",
        description: err.message || "네트워크 통신 오류가 발생했습니다."
      })
    } finally {
      setIsSaving(false)
    }
  }

  if (isAuthLoading || isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-80" />
        </div>
        <div className="flex gap-4 border-b border-border pb-2">
          <Skeleton className="h-9 w-28" />
          <Skeleton className="h-9 w-28" />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  if (role !== "expert") {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-card border border-border rounded-xl text-center min-h-[400px]">
        <h3 className="text-lg font-bold text-foreground mb-1">접근 권한 없음</h3>
        <p className="text-sm text-muted-foreground">전문가 회원만 관심 업종을 설정할 수 있습니다.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-foreground">관심 업종 및 뉴스 소스 설정</h1>
        <p className="text-sm text-muted-foreground mt-1">
          뉴스 소스를 선택한 뒤 식품 유형을 설정하고 저장하면 맞춤형 일일 브리핑 리포트가 생성됩니다.
        </p>
      </div>

      {/* Custom Styled Tabs */}
      <div className="flex border-b border-border/80 gap-2">
        <button
          onClick={() => setActiveTab("media")}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-all duration-200 focus:outline-none",
            activeTab === "media"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
        >
          <Newspaper className="h-4 w-4" />
          뉴스 소스 · {selectedMedia.length}개 선택 (1~3)
        </button>
        <button
          onClick={handleFoodtypeTabClick}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-all duration-200 focus:outline-none",
            activeTab === "foodtype"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
        >
          <Utensils className="h-4 w-4" />
          식품 유형 · {selectedFoodParents.length}개 선택 (1~3)
        </button>
      </div>

      {/* Tab Contents: Media */}
      {activeTab === "media" && (
        <div className="space-y-4">
          <div className="p-4 bg-muted/20 border border-border/60 rounded-xl flex items-start gap-3">
            <AlertTriangle className="h-4.5 w-4.5 text-primary shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <h4 className="text-xs font-bold text-foreground">뉴스 소스 선택 규칙</h4>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                관심 채널 업종 섹션입니다. 관심 분야를 <strong>1~3개</strong> 자유롭게 선택하세요.
                1개만 골라도 저장할 수 있습니다. 일부 채널은 별도 선택 없이 리포트에 항상 포함됩니다.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {mediaCategories.map((media) => {
              const isSelected = selectedMedia.includes(media.code)
              return (
                <div
                  key={media.code}
                  onClick={() => handleMediaToggle(media.code)}
                  className={cn(
                    "flex flex-col justify-between p-4 border rounded-xl cursor-pointer select-none transition-all duration-200 shadow-xs",
                    isSelected
                      ? "border-primary bg-primary/5 text-primary"
                      : "border-border hover:border-primary/30 hover:bg-muted/20 text-foreground"
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-bold leading-snug">{media.name_ko}</span>
                    <div
                      className={cn(
                        "h-4 w-4 rounded-full border flex items-center justify-center shrink-0",
                        isSelected
                          ? "border-primary bg-primary text-primary-foreground"
                          : "border-muted-foreground/30"
                      )}
                    >
                      {isSelected && <Check className="h-2.5 w-2.5 stroke-[3]" />}
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1">
                    {media.keywords.slice(0, 3).map((kw, idx) => (
                      <Badge key={idx} variant="outline" className={cn("text-[9px] border-none px-1 py-0", isSelected ? "bg-primary/15 text-primary" : "bg-muted/65 text-muted-foreground")}>
                        #{kw}
                      </Badge>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>

          <div className="pt-4 flex justify-end">
            <Button
              type="button"
              onClick={handleMediaNext}
              className="bg-primary text-primary-foreground hover:bg-primary/95 text-xs h-9.5 px-6 font-bold"
            >
              다음
              <ArrowRight className="h-3.5 w-3.5 ml-1.5" />
            </Button>
          </div>
        </div>
      )}

      {/* Tab Contents: Foodtype */}
      {activeTab === "foodtype" && (
        <div className="space-y-5">
          <div className="p-4 bg-muted/20 border border-border/60 rounded-xl flex items-start gap-3">
            <AlertTriangle className="h-4.5 w-4.5 text-primary shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <h4 className="text-xs font-bold text-foreground">식품 유형 카테고리 구성 규칙</h4>
              <p className="text-[11px] text-muted-foreground leading-relaxed font-medium">
                - 대분류는 <strong>1~3개</strong> 자유롭게 선택할 수 있습니다. 1개만 골라도 저장됩니다.
                <br />
                - 일반 대분류(Standard) 선택 시, 해당 대분류 아래 <strong>중분류를 1~3개</strong> 함께 선택해 주세요.
                <br />
                - 특수 대분류(Flat - <span className="text-primary font-bold">특수영양식품, 특수의료용도식품, 알가공품류, 벌꿀·화분가공품류</span>)는 중분류가 없으며, 선택 시 즉시 확정됩니다.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {foodtypeParents.map((parent) => {
              const isParentSelected = selectedFoodParents.includes(parent.code)
              const selectedChildren = selectedFoodChildren[parent.code] || []
              return (
                <div
                  key={parent.code}
                  onClick={() => handleFoodParentToggle(parent)}
                  className={cn(
                    "flex flex-col justify-between p-4 border rounded-xl cursor-pointer select-none transition-all duration-200 shadow-xs min-h-[5.5rem]",
                    isParentSelected
                      ? "border-primary bg-primary/5 text-primary"
                      : "border-border hover:border-primary/30 hover:bg-muted/20 text-foreground",
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-bold leading-snug">{parent.name_ko}</span>
                    <div
                      className={cn(
                        "h-4 w-4 rounded-full border flex items-center justify-center shrink-0",
                        isParentSelected
                          ? "border-primary bg-primary text-primary-foreground"
                          : "border-muted-foreground/30",
                      )}
                    >
                      {isParentSelected && <Check className="h-2.5 w-2.5 stroke-[3]" />}
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1">
                    {parent.is_flat ? (
                      <Badge
                        variant="outline"
                        className={cn(
                          "text-[9px] border-none px-1 py-0",
                          isParentSelected ? "bg-primary/15 text-primary" : "bg-muted/65 text-muted-foreground",
                        )}
                      >
                        단일(Flat)
                      </Badge>
                    ) : isParentSelected ? (
                      <Badge
                        variant="outline"
                        className="text-[9px] border-none px-1 py-0 bg-primary/15 text-primary"
                      >
                        중분류 {selectedChildren.length}/3
                      </Badge>
                    ) : (
                      parent.keywords.slice(0, 2).map((kw, idx) => (
                        <Badge
                          key={idx}
                          variant="outline"
                          className="text-[9px] border-none px-1 py-0 bg-muted/65 text-muted-foreground"
                        >
                          #{kw}
                        </Badge>
                      ))
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {selectedFoodParents.some((code) => {
            const p = categories.find((c) => c.code === code)
            return p && !p.is_flat
          }) && (
            <div className="space-y-4 pt-2">
              <div className="flex items-center gap-1.5 text-muted-foreground text-[11px] font-semibold">
                <HelpCircle className="h-3.5 w-3.5 text-primary" />
                <span>선택한 대분류의 중분류를 각각 최대 3개까지 선택해 주세요.</span>
              </div>
              {selectedFoodParents.map((parentCode) => {
                const parent = categories.find((c) => c.code === parentCode)
                if (!parent || parent.is_flat) return null
                const childrenOfParent = foodtypeChildren.filter((c) => c.parent_code === parentCode)
                const selectedChildren = selectedFoodChildren[parentCode] || []
                return (
                  <div
                    key={parentCode}
                    className="rounded-xl border border-primary/30 bg-primary/5 p-4 space-y-3"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <h3 className="text-xs font-bold text-primary">{parent.name_ko}</h3>
                      <Badge variant="secondary" className="text-[10px] font-bold border-none bg-primary/15 text-primary">
                        {selectedChildren.length}/3
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
                      {childrenOfParent.map((child) => {
                        const isChildSelected = selectedChildren.includes(child.code)
                        return (
                          <div
                            key={child.code}
                            onClick={() => handleFoodChildToggle(parentCode, child.code)}
                            className={cn(
                              "flex items-center justify-between p-2.5 border rounded-lg cursor-pointer select-none transition-all duration-200 text-xs",
                              isChildSelected
                                ? "border-primary/40 bg-primary/10 text-primary font-bold"
                                : "border-border/60 hover:border-border bg-card hover:bg-muted/40 text-muted-foreground hover:text-foreground",
                            )}
                          >
                            <span className="leading-snug pr-1">{child.name_ko}</span>
                            <div
                              className={cn(
                                "h-3.5 w-3.5 rounded-full border flex items-center justify-center shrink-0",
                                isChildSelected
                                  ? "border-primary bg-primary text-primary-foreground"
                                  : "border-muted-foreground/30",
                              )}
                            >
                              {isChildSelected && <Check className="h-2 w-2 stroke-[3.5]" />}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          <div className="pt-4 flex justify-end">
            <Button
              type="button"
              onClick={() => void handleSave()}
              disabled={isSaving}
              className="bg-primary text-primary-foreground hover:bg-primary/95 text-xs h-9.5 px-6 font-bold"
            >
              {isSaving ? <Spinner className="h-3.5 w-3.5 mr-1.5" /> : <Save className="h-3.5 w-3.5 mr-1.5" />}
              업종 설정 저장하기
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
