#ifndef BASELAYER_H
#define BASELAYER_H
#include <string>
#include <memory>
#include <vector>
#include <algorithm>
#include "utils/tensor.h"
#include "utils/mathhelper.h"

using namespace std;

template<typename T>
class LayerGradient {
public:
    Tensor<T> dx;
    Tensor<T> dWeights;
    Tensor<T> dBias;
};

class BaseLayer
{
public:        
    virtual Tensor<float> ForwardPropagation(const Tensor<float> &input) = 0;
    virtual LayerGradient<float> BackwardPropagation(const LayerGradient<float> &dout) = 0;

    shared_ptr<BaseLayer> GetInputLayer() const { return m_inputLayer;}
    string GetName() const {return m_name;}
    vector<int> GetActivationShape() const {return m_activationShape;}

    const Tensor<float> &GetWeightsRef() const {return ref(m_weights);}
    const Tensor<float> &GetBiasRef() const {return ref(m_bias);}
    const LayerGradient<float> &GetGradientRef() const {return ref(m_gradients);}

    void SetWeights(const Tensor<float> &in){ m_weights = in;}
    void SetBias(const Tensor<float> &in){ m_bias = in;}
    void SetGradient(const LayerGradient<float> &in){ m_gradients = in;}

    bool HasParameter() const { return m_hasParameter;}

    bool IsTraining() const { return m_isTraining;}
    void SetTrainingMode(bool flag){ m_isTraining = flag;}

protected:
    // Weights and bias are references, we don't need to store them
    Tensor<float> m_weights;
    Tensor<float> m_bias;

    // We need to cache the activations and gradients for backprop
    Tensor<float> m_activation;
    Tensor<float> m_previousInput;
    LayerGradient<float> m_gradients;

    vector<int> m_activationShape;

    string m_name;
    bool m_hasParameter = false;

    // Flag to detect if we're on training mode (Used on batch-norm, dropout)
    bool m_isTraining;

    // Reference to layers connected to this current layer    
    shared_ptr<BaseLayer> m_inputLayer = nullptr;
};

#endif // BASELAYER_H
