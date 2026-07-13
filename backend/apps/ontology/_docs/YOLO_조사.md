# YOLO 조사

> 컴퓨터비전 / 컴퓨터비전 YOLO 조사

---

## 요약

Object Detection(객체 검출) 분야의 역사와 방식을 보고, YOLO와 기존 방식의 차이점을 통해 향상된 기능을 이해한다. 아울러 계속 발전하는 객체 검출 방향을 예측해본다.

---

## 목차

1. Object Detection(객체 검출)의 역사
2. Object Detection(객체 검출)의 방식
3. YOLO의 정의
4. CNN계열 Fast R-CNN과 YOLO의 비교
5. YOLO의 발전과정
6. YOLO 조사결과와 의견

---

## 1. Object Detection(객체 검출)의 역사

객체검출은 카메라나 다른 센서를 이용하여 자동차, 사람, 동물, 물건 등을 검출하는 것이다. 컴퓨팅파워가 좋아지기 전에는 이 문제는 모두 영상처리로 풀고 있다가 2012년 AlexNet이 나타나고 부터는 딥러닝을 활용하여 문제를 접근하고 있다.

기존의 영상처리는 정적인 상태를 인식한다. 따라서 하나의 윈도에서 객체 검출을 위한 영역분할을 한다. 하나의 윈도우상에서 물체를 인식하는 것은 알고리즘의 성능이 좋지 않았다. 정지된 객체의 인식과 대상 조작에 있어서 정확도가 많이 떨어졌다.

이를 해결하기 위해 동적인 상태인식을 통해 가상의 깊이 정보를 정의하도록 시도했다. 이를 위해 다계층 중첩 윈도우를 적용한다. 그리고 다계층 중첩 윈도우 영역간의 교차영역을 지정하여 정확도를 올릴 수 있었다. 근래에는 밀집한 소형 물체의 정확한 위치 검출을 위한 다계층 중첩 윈도우를 이용한 YOLO 네트워크의 성능개선이 이뤄지고 있다.

---

## 2. Object Detection(객체 검출)의 방식

딥러닝을 사용하는 객체검출 방식으로는 2가지가 있다.

### Two-shot Detection

2단계를 걸쳐서 검출하는 방식이다. 대표적인 신경망은 **R-CNN**이다.

1. **예상범위 추출(RPN)**: Selective Search 알고리즘으로 추려내어 약 2000개의 랜덤사이즈 Bounding Box를 생성
2. 모든 Bounding Box를 CNN으로 전달
3. 여러 번의 네트워크를 통과해야 하므로 연산량이 매우 많아 실시간성이 거의 없음

### One-shot Detection

Input image가 있으면, 하나의 신경망을 통과하여 물체의 bounding box와 class를 동시에 예측하는 방식이다. 대표적으로 **YOLO, SSD, RetinaNet** 등이 있다.

---

## 3. YOLO의 정의

**YOLO**는 **You Only Look Once**의 약어로, Joseph Redmon이 워싱턴 대학교에서 여러 친구들과 함께 2015년에 YOLOv1을 처음 논문과 함께 발표했다. 당시만 해도 Object Detection에서는 대부분 Faster R-CNN(Region with Convolutional Neural Network)가 가장 좋은 성능을 내고 있었다.

Yolo는 처음으로 **One-shot-detection** 방법을 고안하였다. 이전까지는 CNN 계열에서는 Two-shot-detection으로 Object Detection을 구성하였다. 그러나 실시간성이 굉장히 부족하다는 단점이 있었다.

---

## 4. CNN계열 Fast R-CNN과 YOLO의 비교

| 구분 | Fast R-CNN | YOLO |
|------|-----------|------|
| 장점 | 높은 이미지 분류 정확도 | 합성곱 신경망을 단 한 번 통과, 임의 상품에 피팅 가능 |
| 단점 | 과도한 오버헤드 발생, 시간 소모, 현실 적용 어려움 | 학습정도와 이미지 크기에 따라 모델 성능 저하 |

- **R-CNN → Fast R-CNN → Faster R-CNN → YOLO**: 각 단계별로 대략 10배씩 속도 차이가 남
- YOLO가 등장하여 45 FPS를 보여주었고, 빠른 버전의 경우 155 FPS를 기록함

### Error Analysis 비교 (Fast R-CNN vs YOLO)

| 오류 유형 | Fast R-CNN | YOLO |
|----------|-----------|------|
| Background | 13.6% | 4.75% |
| Other | 1.9% | 4.0% |
| Sim | 4.3% | 6.75% |
| Loc | 8.6% | 19.0% |
| Correct | 71.6% | 65.5% |

---

## 5. YOLO의 발전과정

### YOLO v1

- 네트워크 구조는 이미지 분류를 위해 설계된 **GoogleNet 모델 기반**
- 24개의 콘볼루션 계층과 2개의 완전히 연결된 계층으로 구성
- 풀링 계층은 사용하지 않음

### YOLO v2

- 대량의 분류 데이터를 활용하기 위해 고안된 방법
- YOLO v1에 비해 정확도와 속도 향상을 위해 **일괄 정규화 계층** 추가
- 경계 박스의 예측을 완전히 연결된 계층 대신에 **앵커박스**에서 수행하여 네트워크를 축소하면서 출력 해상도를 향상

### YOLO v3

- **로지스틱 회귀(Logistic Regression)**를 적용하여 경계 박스의 객관성 점수(Objectness Score)를 예측
- 경계 박스 예측, 클래스 예측, 특징 검출기 및 반복적 검출 방지를 개선
- 결합된 특징 맵을 처리하고 보다 큰 텐서를 예측하기 위해 추가적인 콘볼루션 계층 포함

### YOLO v4

- YOLOv3 이후에 나온 딥러닝의 정확도를 개선하는 다양한 방법을 적용해 YOLO의 성능을 극대화
- 대표적인 모듈인 **SPP**: 딥러닝에 최적화하기 위해 CNN과 SPM을 결합하고 bag-of-word 대신 maxpooling 사용
- 테스트 성능 결과 기존 v3와 비교해서 약 7% 추론시간이 증가하지만 **5.7% 정확도 향상**

### YOLO v5

- YOLOv3를 **PyTorch**로 구현한 모듈
- FPS와 mAP 측면에서 모두 뛰어난 성능 발휘
- 아키텍처 부분은 **CSPNet(BottleneckCSP)** 사용
  - 논문명: *CSPNET: A NEW BACKBONE THAT CAN ENHANCE LEARNING CAPABILITY OF CNN*
  - CNN의 학습능력을 향상시킬 수 있는 새로운 백본으로 정의

---

## 6. YOLO 조사결과와 의견

최근 객체 검출 분야에 있어서 딥러닝 알고리즘은 없어서는 안 되는 중요한 요소이다. 이들 중에서 YOLO 네트워크는 딥러닝 네트워크의 단점인 느린 처리속도를 획기적으로 줄임으로써 주목받고 있다.

데이터의 공급이 인공지능의 성능을 올리는 포커스임은 분명하다. 이론에 머무르지 않고, 현실에 바로 적용 가능한 신경망 메소드를 통해 동적이미지 인식의 방법을 이해할 수 있었다.

하지만, YOLO 네트워크는 다른 딥러닝 알고리즘에 비해 **검출율이 비교적 낮다는 단점**을 가지고 있다. 특히 소형 오브젝트에 대해서는 더욱 검출 성능이 낮아진다는 의견이 많다.

YOLO 네트워크가 갖고 있는 소형 물체의 높은 미검출이나 밀집된 상황에서 오검출과 같은 단점들을 개선하기 위해, **다계층 중첩 윈도우 기반 알고리즘으로 진화**하는 것으로 예측이 된다.

---

## 주요 논문 출처 및 연구 논문 참고

**객체검출의 역사**
- Object Detection in 20 Years: A Survey — https://arxiv.org/pdf/1905.05055.pdf

**Object Detection(객체 검출)의 방식**
- https://mickael-k.tistory.com/24?category=798521

**연구 논문**
1. 밀집한 소형 물체의 정확한 위치 검출을 위한 다계층 중첩 윈도우를 이용한 YOLO 네트워크의 성능개선 (유재형, 한영준, 한헌수)
2. 객체 검출을 위한 CNN과 YOLO 성능 비교 실험 (원광대학교 디지털콘텐츠공학과, 이용환, 김영섭)
3. VITON: An Image-based Virtual Try-on Network
4. Self-Correction for Human Parsing, Peike Li1
5. Devil in the Details: Towards Accurate Single and Multiple Human Parsing
