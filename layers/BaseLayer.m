classdef (Abstract) BaseLayer < handle
    %BASELAYER Abstract class for Layer
    % Check format on reference project:
    % http://cs.stanford.edu/people/karpathy/convnetjs/
    % https://github.com/karpathy/convnetjs
    % https://databoys.github.io/Feedforward/
    % http://scs.ryerson.ca/~aharley/neural-networks/
    
    properties (Abstract, Access = 'protected')
        weights
        biases
        activations
        gradients
        config
        previousInput
        name
        index
        activationShape
        inputLayer
        weightShape
    end
    
    properties (Access = 'public')
        doGradientCheck = false;
    end
    
    properties (Access = 'protected')
        executionTime = 0;
    end
    
    methods(Abstract, Access = 'public')
        % Activations will be a tensor
        [activations] = ForwardPropagation(obj, inputs, weights, bias);
        % Gradient will be a struct with input, bias, weight
        [gradient] = BackwardPropagation(obj);
        [gradient] = EvalBackpropNumerically(obj, dout);
    end
    
    methods(Access = 'public')
        function [exTime] = getExecutionTime(obj)
            exTime = obj.executionTime;
        end
        
        function [activations] = getActivations(obj)
            activations = obj.activations;
        end
        
        function [gradients] = getGradients(obj)
            gradients = obj.gradients;
        end
        
        function [config] = getConfig(obj)
            config = obj.config;
        end
        
        function [index] = getIndex(obj)
            index = obj.index;
        end
        
        function [name] = getName(obj)
            name = obj.name;
        end
        
        function [actShape] = getActivationShape(obj)
            actShape = obj.activationShape;
        end
        
        function [weightShape] = getWeightShape(obj)
            weightShape = obj.weightShape;
        end
        
        function [layer] = getInputLayer(obj)
            layer = obj.inputLayer;
        end
        
        function [weights] = getWeights(obj)
            weights = obj.weights;
        end
        
        function [bias] = getBias(obj)
            bias = obj.biases;
        end
        
        function EnableGradientCheck(obj, flag)
            obj.doGradientCheck = flag;
        end
        
        function numInputs = GetNumInputs(obj)
            numInputs = numel(obj.inputLayer);
        end
        
    end
    
end