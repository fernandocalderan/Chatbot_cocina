function K_(I) {
  return I && I.__esModule && Object.prototype.hasOwnProperty.call(I, "default") ? I.default : I;
}
var fE = { exports: {} }, Xp = {}, dE = { exports: {} }, St = {};
/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var KR;
function q_() {
  if (KR) return St;
  KR = 1;
  var I = Symbol.for("react.element"), j = Symbol.for("react.portal"), k = Symbol.for("react.fragment"), Te = Symbol.for("react.strict_mode"), Fe = Symbol.for("react.profiler"), Ee = Symbol.for("react.provider"), S = Symbol.for("react.context"), Et = Symbol.for("react.forward_ref"), se = Symbol.for("react.suspense"), ce = Symbol.for("react.memo"), tt = Symbol.for("react.lazy"), J = Symbol.iterator;
  function Se(_) {
    return _ === null || typeof _ != "object" ? null : (_ = J && _[J] || _["@@iterator"], typeof _ == "function" ? _ : null);
  }
  var ae = { isMounted: function() {
    return !1;
  }, enqueueForceUpdate: function() {
  }, enqueueReplaceState: function() {
  }, enqueueSetState: function() {
  } }, Ve = Object.assign, at = {};
  function ct(_, V, Ie) {
    this.props = _, this.context = V, this.refs = at, this.updater = Ie || ae;
  }
  ct.prototype.isReactComponent = {}, ct.prototype.setState = function(_, V) {
    if (typeof _ != "object" && typeof _ != "function" && _ != null) throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");
    this.updater.enqueueSetState(this, _, V, "setState");
  }, ct.prototype.forceUpdate = function(_) {
    this.updater.enqueueForceUpdate(this, _, "forceUpdate");
  };
  function gt() {
  }
  gt.prototype = ct.prototype;
  function qe(_, V, Ie) {
    this.props = _, this.context = V, this.refs = at, this.updater = Ie || ae;
  }
  var Le = qe.prototype = new gt();
  Le.constructor = qe, Ve(Le, ct.prototype), Le.isPureReactComponent = !0;
  var it = Array.isArray, ke = Object.prototype.hasOwnProperty, Qe = { current: null }, He = { key: !0, ref: !0, __self: !0, __source: !0 };
  function ln(_, V, Ie) {
    var Pe, ft = {}, lt = null, nt = null;
    if (V != null) for (Pe in V.ref !== void 0 && (nt = V.ref), V.key !== void 0 && (lt = "" + V.key), V) ke.call(V, Pe) && !He.hasOwnProperty(Pe) && (ft[Pe] = V[Pe]);
    var ut = arguments.length - 2;
    if (ut === 1) ft.children = Ie;
    else if (1 < ut) {
      for (var dt = Array(ut), It = 0; It < ut; It++) dt[It] = arguments[It + 2];
      ft.children = dt;
    }
    if (_ && _.defaultProps) for (Pe in ut = _.defaultProps, ut) ft[Pe] === void 0 && (ft[Pe] = ut[Pe]);
    return { $$typeof: I, type: _, key: lt, ref: nt, props: ft, _owner: Qe.current };
  }
  function Pt(_, V) {
    return { $$typeof: I, type: _.type, key: V, ref: _.ref, props: _.props, _owner: _._owner };
  }
  function Jt(_) {
    return typeof _ == "object" && _ !== null && _.$$typeof === I;
  }
  function un(_) {
    var V = { "=": "=0", ":": "=2" };
    return "$" + _.replace(/[=:]/g, function(Ie) {
      return V[Ie];
    });
  }
  var _t = /\/+/g;
  function Me(_, V) {
    return typeof _ == "object" && _ !== null && _.key != null ? un("" + _.key) : V.toString(36);
  }
  function Ft(_, V, Ie, Pe, ft) {
    var lt = typeof _;
    (lt === "undefined" || lt === "boolean") && (_ = null);
    var nt = !1;
    if (_ === null) nt = !0;
    else switch (lt) {
      case "string":
      case "number":
        nt = !0;
        break;
      case "object":
        switch (_.$$typeof) {
          case I:
          case j:
            nt = !0;
        }
    }
    if (nt) return nt = _, ft = ft(nt), _ = Pe === "" ? "." + Me(nt, 0) : Pe, it(ft) ? (Ie = "", _ != null && (Ie = _.replace(_t, "$&/") + "/"), Ft(ft, V, Ie, "", function(It) {
      return It;
    })) : ft != null && (Jt(ft) && (ft = Pt(ft, Ie + (!ft.key || nt && nt.key === ft.key ? "" : ("" + ft.key).replace(_t, "$&/") + "/") + _)), V.push(ft)), 1;
    if (nt = 0, Pe = Pe === "" ? "." : Pe + ":", it(_)) for (var ut = 0; ut < _.length; ut++) {
      lt = _[ut];
      var dt = Pe + Me(lt, ut);
      nt += Ft(lt, V, Ie, dt, ft);
    }
    else if (dt = Se(_), typeof dt == "function") for (_ = dt.call(_), ut = 0; !(lt = _.next()).done; ) lt = lt.value, dt = Pe + Me(lt, ut++), nt += Ft(lt, V, Ie, dt, ft);
    else if (lt === "object") throw V = String(_), Error("Objects are not valid as a React child (found: " + (V === "[object Object]" ? "object with keys {" + Object.keys(_).join(", ") + "}" : V) + "). If you meant to render a collection of children, use an array instead.");
    return nt;
  }
  function kt(_, V, Ie) {
    if (_ == null) return _;
    var Pe = [], ft = 0;
    return Ft(_, Pe, "", "", function(lt) {
      return V.call(Ie, lt, ft++);
    }), Pe;
  }
  function Ot(_) {
    if (_._status === -1) {
      var V = _._result;
      V = V(), V.then(function(Ie) {
        (_._status === 0 || _._status === -1) && (_._status = 1, _._result = Ie);
      }, function(Ie) {
        (_._status === 0 || _._status === -1) && (_._status = 2, _._result = Ie);
      }), _._status === -1 && (_._status = 0, _._result = V);
    }
    if (_._status === 1) return _._result.default;
    throw _._result;
  }
  var Re = { current: null }, Z = { transition: null }, we = { ReactCurrentDispatcher: Re, ReactCurrentBatchConfig: Z, ReactCurrentOwner: Qe };
  function ne() {
    throw Error("act(...) is not supported in production builds of React.");
  }
  return St.Children = { map: kt, forEach: function(_, V, Ie) {
    kt(_, function() {
      V.apply(this, arguments);
    }, Ie);
  }, count: function(_) {
    var V = 0;
    return kt(_, function() {
      V++;
    }), V;
  }, toArray: function(_) {
    return kt(_, function(V) {
      return V;
    }) || [];
  }, only: function(_) {
    if (!Jt(_)) throw Error("React.Children.only expected to receive a single React element child.");
    return _;
  } }, St.Component = ct, St.Fragment = k, St.Profiler = Fe, St.PureComponent = qe, St.StrictMode = Te, St.Suspense = se, St.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = we, St.act = ne, St.cloneElement = function(_, V, Ie) {
    if (_ == null) throw Error("React.cloneElement(...): The argument must be a React element, but you passed " + _ + ".");
    var Pe = Ve({}, _.props), ft = _.key, lt = _.ref, nt = _._owner;
    if (V != null) {
      if (V.ref !== void 0 && (lt = V.ref, nt = Qe.current), V.key !== void 0 && (ft = "" + V.key), _.type && _.type.defaultProps) var ut = _.type.defaultProps;
      for (dt in V) ke.call(V, dt) && !He.hasOwnProperty(dt) && (Pe[dt] = V[dt] === void 0 && ut !== void 0 ? ut[dt] : V[dt]);
    }
    var dt = arguments.length - 2;
    if (dt === 1) Pe.children = Ie;
    else if (1 < dt) {
      ut = Array(dt);
      for (var It = 0; It < dt; It++) ut[It] = arguments[It + 2];
      Pe.children = ut;
    }
    return { $$typeof: I, type: _.type, key: ft, ref: lt, props: Pe, _owner: nt };
  }, St.createContext = function(_) {
    return _ = { $$typeof: S, _currentValue: _, _currentValue2: _, _threadCount: 0, Provider: null, Consumer: null, _defaultValue: null, _globalName: null }, _.Provider = { $$typeof: Ee, _context: _ }, _.Consumer = _;
  }, St.createElement = ln, St.createFactory = function(_) {
    var V = ln.bind(null, _);
    return V.type = _, V;
  }, St.createRef = function() {
    return { current: null };
  }, St.forwardRef = function(_) {
    return { $$typeof: Et, render: _ };
  }, St.isValidElement = Jt, St.lazy = function(_) {
    return { $$typeof: tt, _payload: { _status: -1, _result: _ }, _init: Ot };
  }, St.memo = function(_, V) {
    return { $$typeof: ce, type: _, compare: V === void 0 ? null : V };
  }, St.startTransition = function(_) {
    var V = Z.transition;
    Z.transition = {};
    try {
      _();
    } finally {
      Z.transition = V;
    }
  }, St.unstable_act = ne, St.useCallback = function(_, V) {
    return Re.current.useCallback(_, V);
  }, St.useContext = function(_) {
    return Re.current.useContext(_);
  }, St.useDebugValue = function() {
  }, St.useDeferredValue = function(_) {
    return Re.current.useDeferredValue(_);
  }, St.useEffect = function(_, V) {
    return Re.current.useEffect(_, V);
  }, St.useId = function() {
    return Re.current.useId();
  }, St.useImperativeHandle = function(_, V, Ie) {
    return Re.current.useImperativeHandle(_, V, Ie);
  }, St.useInsertionEffect = function(_, V) {
    return Re.current.useInsertionEffect(_, V);
  }, St.useLayoutEffect = function(_, V) {
    return Re.current.useLayoutEffect(_, V);
  }, St.useMemo = function(_, V) {
    return Re.current.useMemo(_, V);
  }, St.useReducer = function(_, V, Ie) {
    return Re.current.useReducer(_, V, Ie);
  }, St.useRef = function(_) {
    return Re.current.useRef(_);
  }, St.useState = function(_) {
    return Re.current.useState(_);
  }, St.useSyncExternalStore = function(_, V, Ie) {
    return Re.current.useSyncExternalStore(_, V, Ie);
  }, St.useTransition = function() {
    return Re.current.useTransition();
  }, St.version = "18.3.1", St;
}
var Jp = { exports: {} };
/**
 * @license React
 * react.development.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
Jp.exports;
var qR;
function X_() {
  return qR || (qR = 1, function(I, j) {
    process.env.NODE_ENV !== "production" && function() {
      typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart == "function" && __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart(new Error());
      var k = "18.3.1", Te = Symbol.for("react.element"), Fe = Symbol.for("react.portal"), Ee = Symbol.for("react.fragment"), S = Symbol.for("react.strict_mode"), Et = Symbol.for("react.profiler"), se = Symbol.for("react.provider"), ce = Symbol.for("react.context"), tt = Symbol.for("react.forward_ref"), J = Symbol.for("react.suspense"), Se = Symbol.for("react.suspense_list"), ae = Symbol.for("react.memo"), Ve = Symbol.for("react.lazy"), at = Symbol.for("react.offscreen"), ct = Symbol.iterator, gt = "@@iterator";
      function qe(h) {
        if (h === null || typeof h != "object")
          return null;
        var C = ct && h[ct] || h[gt];
        return typeof C == "function" ? C : null;
      }
      var Le = {
        /**
         * @internal
         * @type {ReactComponent}
         */
        current: null
      }, it = {
        transition: null
      }, ke = {
        current: null,
        // Used to reproduce behavior of `batchedUpdates` in legacy mode.
        isBatchingLegacy: !1,
        didScheduleLegacyUpdate: !1
      }, Qe = {
        /**
         * @internal
         * @type {ReactComponent}
         */
        current: null
      }, He = {}, ln = null;
      function Pt(h) {
        ln = h;
      }
      He.setExtraStackFrame = function(h) {
        ln = h;
      }, He.getCurrentStack = null, He.getStackAddendum = function() {
        var h = "";
        ln && (h += ln);
        var C = He.getCurrentStack;
        return C && (h += C() || ""), h;
      };
      var Jt = !1, un = !1, _t = !1, Me = !1, Ft = !1, kt = {
        ReactCurrentDispatcher: Le,
        ReactCurrentBatchConfig: it,
        ReactCurrentOwner: Qe
      };
      kt.ReactDebugCurrentFrame = He, kt.ReactCurrentActQueue = ke;
      function Ot(h) {
        {
          for (var C = arguments.length, z = new Array(C > 1 ? C - 1 : 0), F = 1; F < C; F++)
            z[F - 1] = arguments[F];
          Z("warn", h, z);
        }
      }
      function Re(h) {
        {
          for (var C = arguments.length, z = new Array(C > 1 ? C - 1 : 0), F = 1; F < C; F++)
            z[F - 1] = arguments[F];
          Z("error", h, z);
        }
      }
      function Z(h, C, z) {
        {
          var F = kt.ReactDebugCurrentFrame, X = F.getStackAddendum();
          X !== "" && (C += "%s", z = z.concat([X]));
          var Ne = z.map(function(re) {
            return String(re);
          });
          Ne.unshift("Warning: " + C), Function.prototype.apply.call(console[h], console, Ne);
        }
      }
      var we = {};
      function ne(h, C) {
        {
          var z = h.constructor, F = z && (z.displayName || z.name) || "ReactClass", X = F + "." + C;
          if (we[X])
            return;
          Re("Can't call %s on a component that is not yet mounted. This is a no-op, but it might indicate a bug in your application. Instead, assign to `this.state` directly or define a `state = {};` class property with the desired state in the %s component.", C, F), we[X] = !0;
        }
      }
      var _ = {
        /**
         * Checks whether or not this composite component is mounted.
         * @param {ReactClass} publicInstance The instance we want to test.
         * @return {boolean} True if mounted, false otherwise.
         * @protected
         * @final
         */
        isMounted: function(h) {
          return !1;
        },
        /**
         * Forces an update. This should only be invoked when it is known with
         * certainty that we are **not** in a DOM transaction.
         *
         * You may want to call this when you know that some deeper aspect of the
         * component's state has changed but `setState` was not called.
         *
         * This will not invoke `shouldComponentUpdate`, but it will invoke
         * `componentWillUpdate` and `componentDidUpdate`.
         *
         * @param {ReactClass} publicInstance The instance that should rerender.
         * @param {?function} callback Called after component is updated.
         * @param {?string} callerName name of the calling function in the public API.
         * @internal
         */
        enqueueForceUpdate: function(h, C, z) {
          ne(h, "forceUpdate");
        },
        /**
         * Replaces all of the state. Always use this or `setState` to mutate state.
         * You should treat `this.state` as immutable.
         *
         * There is no guarantee that `this.state` will be immediately updated, so
         * accessing `this.state` after calling this method may return the old value.
         *
         * @param {ReactClass} publicInstance The instance that should rerender.
         * @param {object} completeState Next state.
         * @param {?function} callback Called after component is updated.
         * @param {?string} callerName name of the calling function in the public API.
         * @internal
         */
        enqueueReplaceState: function(h, C, z, F) {
          ne(h, "replaceState");
        },
        /**
         * Sets a subset of the state. This only exists because _pendingState is
         * internal. This provides a merging strategy that is not available to deep
         * properties which is confusing. TODO: Expose pendingState or don't use it
         * during the merge.
         *
         * @param {ReactClass} publicInstance The instance that should rerender.
         * @param {object} partialState Next partial state to be merged with state.
         * @param {?function} callback Called after component is updated.
         * @param {?string} Name of the calling function in the public API.
         * @internal
         */
        enqueueSetState: function(h, C, z, F) {
          ne(h, "setState");
        }
      }, V = Object.assign, Ie = {};
      Object.freeze(Ie);
      function Pe(h, C, z) {
        this.props = h, this.context = C, this.refs = Ie, this.updater = z || _;
      }
      Pe.prototype.isReactComponent = {}, Pe.prototype.setState = function(h, C) {
        if (typeof h != "object" && typeof h != "function" && h != null)
          throw new Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");
        this.updater.enqueueSetState(this, h, C, "setState");
      }, Pe.prototype.forceUpdate = function(h) {
        this.updater.enqueueForceUpdate(this, h, "forceUpdate");
      };
      {
        var ft = {
          isMounted: ["isMounted", "Instead, make sure to clean up subscriptions and pending requests in componentWillUnmount to prevent memory leaks."],
          replaceState: ["replaceState", "Refactor your code to use setState instead (see https://github.com/facebook/react/issues/3236)."]
        }, lt = function(h, C) {
          Object.defineProperty(Pe.prototype, h, {
            get: function() {
              Ot("%s(...) is deprecated in plain JavaScript React classes. %s", C[0], C[1]);
            }
          });
        };
        for (var nt in ft)
          ft.hasOwnProperty(nt) && lt(nt, ft[nt]);
      }
      function ut() {
      }
      ut.prototype = Pe.prototype;
      function dt(h, C, z) {
        this.props = h, this.context = C, this.refs = Ie, this.updater = z || _;
      }
      var It = dt.prototype = new ut();
      It.constructor = dt, V(It, Pe.prototype), It.isPureReactComponent = !0;
      function On() {
        var h = {
          current: null
        };
        return Object.seal(h), h;
      }
      var xr = Array.isArray;
      function Cn(h) {
        return xr(h);
      }
      function nr(h) {
        {
          var C = typeof Symbol == "function" && Symbol.toStringTag, z = C && h[Symbol.toStringTag] || h.constructor.name || "Object";
          return z;
        }
      }
      function Vn(h) {
        try {
          return Bn(h), !1;
        } catch {
          return !0;
        }
      }
      function Bn(h) {
        return "" + h;
      }
      function Yr(h) {
        if (Vn(h))
          return Re("The provided key is an unsupported type %s. This value must be coerced to a string before before using it here.", nr(h)), Bn(h);
      }
      function ci(h, C, z) {
        var F = h.displayName;
        if (F)
          return F;
        var X = C.displayName || C.name || "";
        return X !== "" ? z + "(" + X + ")" : z;
      }
      function oa(h) {
        return h.displayName || "Context";
      }
      function Kn(h) {
        if (h == null)
          return null;
        if (typeof h.tag == "number" && Re("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue."), typeof h == "function")
          return h.displayName || h.name || null;
        if (typeof h == "string")
          return h;
        switch (h) {
          case Ee:
            return "Fragment";
          case Fe:
            return "Portal";
          case Et:
            return "Profiler";
          case S:
            return "StrictMode";
          case J:
            return "Suspense";
          case Se:
            return "SuspenseList";
        }
        if (typeof h == "object")
          switch (h.$$typeof) {
            case ce:
              var C = h;
              return oa(C) + ".Consumer";
            case se:
              var z = h;
              return oa(z._context) + ".Provider";
            case tt:
              return ci(h, h.render, "ForwardRef");
            case ae:
              var F = h.displayName || null;
              return F !== null ? F : Kn(h.type) || "Memo";
            case Ve: {
              var X = h, Ne = X._payload, re = X._init;
              try {
                return Kn(re(Ne));
              } catch {
                return null;
              }
            }
          }
        return null;
      }
      var Rn = Object.prototype.hasOwnProperty, In = {
        key: !0,
        ref: !0,
        __self: !0,
        __source: !0
      }, gr, $a, Ln;
      Ln = {};
      function Sr(h) {
        if (Rn.call(h, "ref")) {
          var C = Object.getOwnPropertyDescriptor(h, "ref").get;
          if (C && C.isReactWarning)
            return !1;
        }
        return h.ref !== void 0;
      }
      function sa(h) {
        if (Rn.call(h, "key")) {
          var C = Object.getOwnPropertyDescriptor(h, "key").get;
          if (C && C.isReactWarning)
            return !1;
        }
        return h.key !== void 0;
      }
      function Qa(h, C) {
        var z = function() {
          gr || (gr = !0, Re("%s: `key` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://reactjs.org/link/special-props)", C));
        };
        z.isReactWarning = !0, Object.defineProperty(h, "key", {
          get: z,
          configurable: !0
        });
      }
      function fi(h, C) {
        var z = function() {
          $a || ($a = !0, Re("%s: `ref` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://reactjs.org/link/special-props)", C));
        };
        z.isReactWarning = !0, Object.defineProperty(h, "ref", {
          get: z,
          configurable: !0
        });
      }
      function ee(h) {
        if (typeof h.ref == "string" && Qe.current && h.__self && Qe.current.stateNode !== h.__self) {
          var C = Kn(Qe.current.type);
          Ln[C] || (Re('Component "%s" contains the string ref "%s". Support for string refs will be removed in a future major release. This case cannot be automatically converted to an arrow function. We ask you to manually fix this case by using useRef() or createRef() instead. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-string-ref', C, h.ref), Ln[C] = !0);
        }
      }
      var xe = function(h, C, z, F, X, Ne, re) {
        var Ae = {
          // This tag allows us to uniquely identify this as a React Element
          $$typeof: Te,
          // Built-in properties that belong on the element
          type: h,
          key: C,
          ref: z,
          props: re,
          // Record the component responsible for creating this element.
          _owner: Ne
        };
        return Ae._store = {}, Object.defineProperty(Ae._store, "validated", {
          configurable: !1,
          enumerable: !1,
          writable: !0,
          value: !1
        }), Object.defineProperty(Ae, "_self", {
          configurable: !1,
          enumerable: !1,
          writable: !1,
          value: F
        }), Object.defineProperty(Ae, "_source", {
          configurable: !1,
          enumerable: !1,
          writable: !1,
          value: X
        }), Object.freeze && (Object.freeze(Ae.props), Object.freeze(Ae)), Ae;
      };
      function ot(h, C, z) {
        var F, X = {}, Ne = null, re = null, Ae = null, mt = null;
        if (C != null) {
          Sr(C) && (re = C.ref, ee(C)), sa(C) && (Yr(C.key), Ne = "" + C.key), Ae = C.__self === void 0 ? null : C.__self, mt = C.__source === void 0 ? null : C.__source;
          for (F in C)
            Rn.call(C, F) && !In.hasOwnProperty(F) && (X[F] = C[F]);
        }
        var bt = arguments.length - 2;
        if (bt === 1)
          X.children = z;
        else if (bt > 1) {
          for (var rn = Array(bt), Wt = 0; Wt < bt; Wt++)
            rn[Wt] = arguments[Wt + 2];
          Object.freeze && Object.freeze(rn), X.children = rn;
        }
        if (h && h.defaultProps) {
          var st = h.defaultProps;
          for (F in st)
            X[F] === void 0 && (X[F] = st[F]);
        }
        if (Ne || re) {
          var Gt = typeof h == "function" ? h.displayName || h.name || "Unknown" : h;
          Ne && Qa(X, Gt), re && fi(X, Gt);
        }
        return xe(h, Ne, re, Ae, mt, Qe.current, X);
      }
      function Ht(h, C) {
        var z = xe(h.type, C, h.ref, h._self, h._source, h._owner, h.props);
        return z;
      }
      function en(h, C, z) {
        if (h == null)
          throw new Error("React.cloneElement(...): The argument must be a React element, but you passed " + h + ".");
        var F, X = V({}, h.props), Ne = h.key, re = h.ref, Ae = h._self, mt = h._source, bt = h._owner;
        if (C != null) {
          Sr(C) && (re = C.ref, bt = Qe.current), sa(C) && (Yr(C.key), Ne = "" + C.key);
          var rn;
          h.type && h.type.defaultProps && (rn = h.type.defaultProps);
          for (F in C)
            Rn.call(C, F) && !In.hasOwnProperty(F) && (C[F] === void 0 && rn !== void 0 ? X[F] = rn[F] : X[F] = C[F]);
        }
        var Wt = arguments.length - 2;
        if (Wt === 1)
          X.children = z;
        else if (Wt > 1) {
          for (var st = Array(Wt), Gt = 0; Gt < Wt; Gt++)
            st[Gt] = arguments[Gt + 2];
          X.children = st;
        }
        return xe(h.type, Ne, re, Ae, mt, bt, X);
      }
      function vn(h) {
        return typeof h == "object" && h !== null && h.$$typeof === Te;
      }
      var on = ".", qn = ":";
      function tn(h) {
        var C = /[=:]/g, z = {
          "=": "=0",
          ":": "=2"
        }, F = h.replace(C, function(X) {
          return z[X];
        });
        return "$" + F;
      }
      var Yt = !1, $t = /\/+/g;
      function ca(h) {
        return h.replace($t, "$&/");
      }
      function Er(h, C) {
        return typeof h == "object" && h !== null && h.key != null ? (Yr(h.key), tn("" + h.key)) : C.toString(36);
      }
      function Ta(h, C, z, F, X) {
        var Ne = typeof h;
        (Ne === "undefined" || Ne === "boolean") && (h = null);
        var re = !1;
        if (h === null)
          re = !0;
        else
          switch (Ne) {
            case "string":
            case "number":
              re = !0;
              break;
            case "object":
              switch (h.$$typeof) {
                case Te:
                case Fe:
                  re = !0;
              }
          }
        if (re) {
          var Ae = h, mt = X(Ae), bt = F === "" ? on + Er(Ae, 0) : F;
          if (Cn(mt)) {
            var rn = "";
            bt != null && (rn = ca(bt) + "/"), Ta(mt, C, rn, "", function(Kf) {
              return Kf;
            });
          } else mt != null && (vn(mt) && (mt.key && (!Ae || Ae.key !== mt.key) && Yr(mt.key), mt = Ht(
            mt,
            // Keep both the (mapped) and old keys if they differ, just as
            // traverseAllChildren used to do for objects as children
            z + // $FlowFixMe Flow incorrectly thinks React.Portal doesn't have a key
            (mt.key && (!Ae || Ae.key !== mt.key) ? (
              // $FlowFixMe Flow incorrectly thinks existing element's key can be a number
              // eslint-disable-next-line react-internal/safe-string-coercion
              ca("" + mt.key) + "/"
            ) : "") + bt
          )), C.push(mt));
          return 1;
        }
        var Wt, st, Gt = 0, hn = F === "" ? on : F + qn;
        if (Cn(h))
          for (var Rl = 0; Rl < h.length; Rl++)
            Wt = h[Rl], st = hn + Er(Wt, Rl), Gt += Ta(Wt, C, z, st, X);
        else {
          var Ko = qe(h);
          if (typeof Ko == "function") {
            var Bi = h;
            Ko === Bi.entries && (Yt || Ot("Using Maps as children is not supported. Use an array of keyed ReactElements instead."), Yt = !0);
            for (var qo = Ko.call(Bi), ou, Gf = 0; !(ou = qo.next()).done; )
              Wt = ou.value, st = hn + Er(Wt, Gf++), Gt += Ta(Wt, C, z, st, X);
          } else if (Ne === "object") {
            var oc = String(h);
            throw new Error("Objects are not valid as a React child (found: " + (oc === "[object Object]" ? "object with keys {" + Object.keys(h).join(", ") + "}" : oc) + "). If you meant to render a collection of children, use an array instead.");
          }
        }
        return Gt;
      }
      function Hi(h, C, z) {
        if (h == null)
          return h;
        var F = [], X = 0;
        return Ta(h, F, "", "", function(Ne) {
          return C.call(z, Ne, X++);
        }), F;
      }
      function Jl(h) {
        var C = 0;
        return Hi(h, function() {
          C++;
        }), C;
      }
      function eu(h, C, z) {
        Hi(h, function() {
          C.apply(this, arguments);
        }, z);
      }
      function pl(h) {
        return Hi(h, function(C) {
          return C;
        }) || [];
      }
      function vl(h) {
        if (!vn(h))
          throw new Error("React.Children.only expected to receive a single React element child.");
        return h;
      }
      function tu(h) {
        var C = {
          $$typeof: ce,
          // As a workaround to support multiple concurrent renderers, we categorize
          // some renderers as primary and others as secondary. We only expect
          // there to be two concurrent renderers at most: React Native (primary) and
          // Fabric (secondary); React DOM (primary) and React ART (secondary).
          // Secondary renderers store their context values on separate fields.
          _currentValue: h,
          _currentValue2: h,
          // Used to track how many concurrent renderers this context currently
          // supports within in a single renderer. Such as parallel server rendering.
          _threadCount: 0,
          // These are circular
          Provider: null,
          Consumer: null,
          // Add these to use same hidden class in VM as ServerContext
          _defaultValue: null,
          _globalName: null
        };
        C.Provider = {
          $$typeof: se,
          _context: C
        };
        var z = !1, F = !1, X = !1;
        {
          var Ne = {
            $$typeof: ce,
            _context: C
          };
          Object.defineProperties(Ne, {
            Provider: {
              get: function() {
                return F || (F = !0, Re("Rendering <Context.Consumer.Provider> is not supported and will be removed in a future major release. Did you mean to render <Context.Provider> instead?")), C.Provider;
              },
              set: function(re) {
                C.Provider = re;
              }
            },
            _currentValue: {
              get: function() {
                return C._currentValue;
              },
              set: function(re) {
                C._currentValue = re;
              }
            },
            _currentValue2: {
              get: function() {
                return C._currentValue2;
              },
              set: function(re) {
                C._currentValue2 = re;
              }
            },
            _threadCount: {
              get: function() {
                return C._threadCount;
              },
              set: function(re) {
                C._threadCount = re;
              }
            },
            Consumer: {
              get: function() {
                return z || (z = !0, Re("Rendering <Context.Consumer.Consumer> is not supported and will be removed in a future major release. Did you mean to render <Context.Consumer> instead?")), C.Consumer;
              }
            },
            displayName: {
              get: function() {
                return C.displayName;
              },
              set: function(re) {
                X || (Ot("Setting `displayName` on Context.Consumer has no effect. You should set it directly on the context with Context.displayName = '%s'.", re), X = !0);
              }
            }
          }), C.Consumer = Ne;
        }
        return C._currentRenderer = null, C._currentRenderer2 = null, C;
      }
      var br = -1, _r = 0, rr = 1, di = 2;
      function Wa(h) {
        if (h._status === br) {
          var C = h._result, z = C();
          if (z.then(function(Ne) {
            if (h._status === _r || h._status === br) {
              var re = h;
              re._status = rr, re._result = Ne;
            }
          }, function(Ne) {
            if (h._status === _r || h._status === br) {
              var re = h;
              re._status = di, re._result = Ne;
            }
          }), h._status === br) {
            var F = h;
            F._status = _r, F._result = z;
          }
        }
        if (h._status === rr) {
          var X = h._result;
          return X === void 0 && Re(`lazy: Expected the result of a dynamic import() call. Instead received: %s

Your code should look like: 
  const MyComponent = lazy(() => import('./MyComponent'))

Did you accidentally put curly braces around the import?`, X), "default" in X || Re(`lazy: Expected the result of a dynamic import() call. Instead received: %s

Your code should look like: 
  const MyComponent = lazy(() => import('./MyComponent'))`, X), X.default;
        } else
          throw h._result;
      }
      function pi(h) {
        var C = {
          // We use these fields to store the result.
          _status: br,
          _result: h
        }, z = {
          $$typeof: Ve,
          _payload: C,
          _init: Wa
        };
        {
          var F, X;
          Object.defineProperties(z, {
            defaultProps: {
              configurable: !0,
              get: function() {
                return F;
              },
              set: function(Ne) {
                Re("React.lazy(...): It is not supported to assign `defaultProps` to a lazy component import. Either specify them where the component is defined, or create a wrapping component around it."), F = Ne, Object.defineProperty(z, "defaultProps", {
                  enumerable: !0
                });
              }
            },
            propTypes: {
              configurable: !0,
              get: function() {
                return X;
              },
              set: function(Ne) {
                Re("React.lazy(...): It is not supported to assign `propTypes` to a lazy component import. Either specify them where the component is defined, or create a wrapping component around it."), X = Ne, Object.defineProperty(z, "propTypes", {
                  enumerable: !0
                });
              }
            }
          });
        }
        return z;
      }
      function vi(h) {
        h != null && h.$$typeof === ae ? Re("forwardRef requires a render function but received a `memo` component. Instead of forwardRef(memo(...)), use memo(forwardRef(...)).") : typeof h != "function" ? Re("forwardRef requires a render function but was given %s.", h === null ? "null" : typeof h) : h.length !== 0 && h.length !== 2 && Re("forwardRef render functions accept exactly two parameters: props and ref. %s", h.length === 1 ? "Did you forget to use the ref parameter?" : "Any additional parameter will be undefined."), h != null && (h.defaultProps != null || h.propTypes != null) && Re("forwardRef render functions do not support propTypes or defaultProps. Did you accidentally pass a React component?");
        var C = {
          $$typeof: tt,
          render: h
        };
        {
          var z;
          Object.defineProperty(C, "displayName", {
            enumerable: !1,
            configurable: !0,
            get: function() {
              return z;
            },
            set: function(F) {
              z = F, !h.name && !h.displayName && (h.displayName = F);
            }
          });
        }
        return C;
      }
      var R;
      R = Symbol.for("react.module.reference");
      function Y(h) {
        return !!(typeof h == "string" || typeof h == "function" || h === Ee || h === Et || Ft || h === S || h === J || h === Se || Me || h === at || Jt || un || _t || typeof h == "object" && h !== null && (h.$$typeof === Ve || h.$$typeof === ae || h.$$typeof === se || h.$$typeof === ce || h.$$typeof === tt || // This needs to include all possible module reference object
        // types supported by any Flight configuration anywhere since
        // we don't know which Flight build this will end up being used
        // with.
        h.$$typeof === R || h.getModuleId !== void 0));
      }
      function ie(h, C) {
        Y(h) || Re("memo: The first argument must be a component. Instead received: %s", h === null ? "null" : typeof h);
        var z = {
          $$typeof: ae,
          type: h,
          compare: C === void 0 ? null : C
        };
        {
          var F;
          Object.defineProperty(z, "displayName", {
            enumerable: !1,
            configurable: !0,
            get: function() {
              return F;
            },
            set: function(X) {
              F = X, !h.name && !h.displayName && (h.displayName = X);
            }
          });
        }
        return z;
      }
      function he() {
        var h = Le.current;
        return h === null && Re(`Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://reactjs.org/link/invalid-hook-call for tips about how to debug and fix this problem.`), h;
      }
      function Ze(h) {
        var C = he();
        if (h._context !== void 0) {
          var z = h._context;
          z.Consumer === h ? Re("Calling useContext(Context.Consumer) is not supported, may cause bugs, and will be removed in a future major release. Did you mean to call useContext(Context) instead?") : z.Provider === h && Re("Calling useContext(Context.Provider) is not supported. Did you mean to call useContext(Context) instead?");
        }
        return C.useContext(h);
      }
      function Ge(h) {
        var C = he();
        return C.useState(h);
      }
      function ht(h, C, z) {
        var F = he();
        return F.useReducer(h, C, z);
      }
      function pt(h) {
        var C = he();
        return C.useRef(h);
      }
      function Tn(h, C) {
        var z = he();
        return z.useEffect(h, C);
      }
      function nn(h, C) {
        var z = he();
        return z.useInsertionEffect(h, C);
      }
      function sn(h, C) {
        var z = he();
        return z.useLayoutEffect(h, C);
      }
      function ar(h, C) {
        var z = he();
        return z.useCallback(h, C);
      }
      function Ga(h, C) {
        var z = he();
        return z.useMemo(h, C);
      }
      function Ka(h, C, z) {
        var F = he();
        return F.useImperativeHandle(h, C, z);
      }
      function Je(h, C) {
        {
          var z = he();
          return z.useDebugValue(h, C);
        }
      }
      function rt() {
        var h = he();
        return h.useTransition();
      }
      function qa(h) {
        var C = he();
        return C.useDeferredValue(h);
      }
      function nu() {
        var h = he();
        return h.useId();
      }
      function ru(h, C, z) {
        var F = he();
        return F.useSyncExternalStore(h, C, z);
      }
      var hl = 0, Wu, ml, $r, $o, kr, lc, uc;
      function Gu() {
      }
      Gu.__reactDisabledLog = !0;
      function yl() {
        {
          if (hl === 0) {
            Wu = console.log, ml = console.info, $r = console.warn, $o = console.error, kr = console.group, lc = console.groupCollapsed, uc = console.groupEnd;
            var h = {
              configurable: !0,
              enumerable: !0,
              value: Gu,
              writable: !0
            };
            Object.defineProperties(console, {
              info: h,
              log: h,
              warn: h,
              error: h,
              group: h,
              groupCollapsed: h,
              groupEnd: h
            });
          }
          hl++;
        }
      }
      function fa() {
        {
          if (hl--, hl === 0) {
            var h = {
              configurable: !0,
              enumerable: !0,
              writable: !0
            };
            Object.defineProperties(console, {
              log: V({}, h, {
                value: Wu
              }),
              info: V({}, h, {
                value: ml
              }),
              warn: V({}, h, {
                value: $r
              }),
              error: V({}, h, {
                value: $o
              }),
              group: V({}, h, {
                value: kr
              }),
              groupCollapsed: V({}, h, {
                value: lc
              }),
              groupEnd: V({}, h, {
                value: uc
              })
            });
          }
          hl < 0 && Re("disabledDepth fell below zero. This is a bug in React. Please file an issue.");
        }
      }
      var Xa = kt.ReactCurrentDispatcher, Za;
      function Ku(h, C, z) {
        {
          if (Za === void 0)
            try {
              throw Error();
            } catch (X) {
              var F = X.stack.trim().match(/\n( *(at )?)/);
              Za = F && F[1] || "";
            }
          return `
` + Za + h;
        }
      }
      var au = !1, gl;
      {
        var qu = typeof WeakMap == "function" ? WeakMap : Map;
        gl = new qu();
      }
      function Xu(h, C) {
        if (!h || au)
          return "";
        {
          var z = gl.get(h);
          if (z !== void 0)
            return z;
        }
        var F;
        au = !0;
        var X = Error.prepareStackTrace;
        Error.prepareStackTrace = void 0;
        var Ne;
        Ne = Xa.current, Xa.current = null, yl();
        try {
          if (C) {
            var re = function() {
              throw Error();
            };
            if (Object.defineProperty(re.prototype, "props", {
              set: function() {
                throw Error();
              }
            }), typeof Reflect == "object" && Reflect.construct) {
              try {
                Reflect.construct(re, []);
              } catch (hn) {
                F = hn;
              }
              Reflect.construct(h, [], re);
            } else {
              try {
                re.call();
              } catch (hn) {
                F = hn;
              }
              h.call(re.prototype);
            }
          } else {
            try {
              throw Error();
            } catch (hn) {
              F = hn;
            }
            h();
          }
        } catch (hn) {
          if (hn && F && typeof hn.stack == "string") {
            for (var Ae = hn.stack.split(`
`), mt = F.stack.split(`
`), bt = Ae.length - 1, rn = mt.length - 1; bt >= 1 && rn >= 0 && Ae[bt] !== mt[rn]; )
              rn--;
            for (; bt >= 1 && rn >= 0; bt--, rn--)
              if (Ae[bt] !== mt[rn]) {
                if (bt !== 1 || rn !== 1)
                  do
                    if (bt--, rn--, rn < 0 || Ae[bt] !== mt[rn]) {
                      var Wt = `
` + Ae[bt].replace(" at new ", " at ");
                      return h.displayName && Wt.includes("<anonymous>") && (Wt = Wt.replace("<anonymous>", h.displayName)), typeof h == "function" && gl.set(h, Wt), Wt;
                    }
                  while (bt >= 1 && rn >= 0);
                break;
              }
          }
        } finally {
          au = !1, Xa.current = Ne, fa(), Error.prepareStackTrace = X;
        }
        var st = h ? h.displayName || h.name : "", Gt = st ? Ku(st) : "";
        return typeof h == "function" && gl.set(h, Gt), Gt;
      }
      function Pi(h, C, z) {
        return Xu(h, !1);
      }
      function Qf(h) {
        var C = h.prototype;
        return !!(C && C.isReactComponent);
      }
      function Vi(h, C, z) {
        if (h == null)
          return "";
        if (typeof h == "function")
          return Xu(h, Qf(h));
        if (typeof h == "string")
          return Ku(h);
        switch (h) {
          case J:
            return Ku("Suspense");
          case Se:
            return Ku("SuspenseList");
        }
        if (typeof h == "object")
          switch (h.$$typeof) {
            case tt:
              return Pi(h.render);
            case ae:
              return Vi(h.type, C, z);
            case Ve: {
              var F = h, X = F._payload, Ne = F._init;
              try {
                return Vi(Ne(X), C, z);
              } catch {
              }
            }
          }
        return "";
      }
      var Lt = {}, Zu = kt.ReactDebugCurrentFrame;
      function xt(h) {
        if (h) {
          var C = h._owner, z = Vi(h.type, h._source, C ? C.type : null);
          Zu.setExtraStackFrame(z);
        } else
          Zu.setExtraStackFrame(null);
      }
      function Qo(h, C, z, F, X) {
        {
          var Ne = Function.call.bind(Rn);
          for (var re in h)
            if (Ne(h, re)) {
              var Ae = void 0;
              try {
                if (typeof h[re] != "function") {
                  var mt = Error((F || "React class") + ": " + z + " type `" + re + "` is invalid; it must be a function, usually from the `prop-types` package, but received `" + typeof h[re] + "`.This often happens because of typos such as `PropTypes.function` instead of `PropTypes.func`.");
                  throw mt.name = "Invariant Violation", mt;
                }
                Ae = h[re](C, re, F, z, null, "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED");
              } catch (bt) {
                Ae = bt;
              }
              Ae && !(Ae instanceof Error) && (xt(X), Re("%s: type specification of %s `%s` is invalid; the type checker function must return `null` or an `Error` but returned a %s. You may have forgotten to pass an argument to the type checker creator (arrayOf, instanceOf, objectOf, oneOf, oneOfType, and shape all require an argument).", F || "React class", z, re, typeof Ae), xt(null)), Ae instanceof Error && !(Ae.message in Lt) && (Lt[Ae.message] = !0, xt(X), Re("Failed %s type: %s", z, Ae.message), xt(null));
            }
        }
      }
      function hi(h) {
        if (h) {
          var C = h._owner, z = Vi(h.type, h._source, C ? C.type : null);
          Pt(z);
        } else
          Pt(null);
      }
      var We;
      We = !1;
      function Ju() {
        if (Qe.current) {
          var h = Kn(Qe.current.type);
          if (h)
            return `

Check the render method of \`` + h + "`.";
        }
        return "";
      }
      function ir(h) {
        if (h !== void 0) {
          var C = h.fileName.replace(/^.*[\\\/]/, ""), z = h.lineNumber;
          return `

Check your code at ` + C + ":" + z + ".";
        }
        return "";
      }
      function mi(h) {
        return h != null ? ir(h.__source) : "";
      }
      var Dr = {};
      function yi(h) {
        var C = Ju();
        if (!C) {
          var z = typeof h == "string" ? h : h.displayName || h.name;
          z && (C = `

Check the top-level render call using <` + z + ">.");
        }
        return C;
      }
      function cn(h, C) {
        if (!(!h._store || h._store.validated || h.key != null)) {
          h._store.validated = !0;
          var z = yi(C);
          if (!Dr[z]) {
            Dr[z] = !0;
            var F = "";
            h && h._owner && h._owner !== Qe.current && (F = " It was passed a child from " + Kn(h._owner.type) + "."), hi(h), Re('Each child in a list should have a unique "key" prop.%s%s See https://reactjs.org/link/warning-keys for more information.', z, F), hi(null);
          }
        }
      }
      function Qt(h, C) {
        if (typeof h == "object") {
          if (Cn(h))
            for (var z = 0; z < h.length; z++) {
              var F = h[z];
              vn(F) && cn(F, C);
            }
          else if (vn(h))
            h._store && (h._store.validated = !0);
          else if (h) {
            var X = qe(h);
            if (typeof X == "function" && X !== h.entries)
              for (var Ne = X.call(h), re; !(re = Ne.next()).done; )
                vn(re.value) && cn(re.value, C);
          }
        }
      }
      function Sl(h) {
        {
          var C = h.type;
          if (C == null || typeof C == "string")
            return;
          var z;
          if (typeof C == "function")
            z = C.propTypes;
          else if (typeof C == "object" && (C.$$typeof === tt || // Note: Memo only checks outer props here.
          // Inner props are checked in the reconciler.
          C.$$typeof === ae))
            z = C.propTypes;
          else
            return;
          if (z) {
            var F = Kn(C);
            Qo(z, h.props, "prop", F, h);
          } else if (C.PropTypes !== void 0 && !We) {
            We = !0;
            var X = Kn(C);
            Re("Component %s declared `PropTypes` instead of `propTypes`. Did you misspell the property assignment?", X || "Unknown");
          }
          typeof C.getDefaultProps == "function" && !C.getDefaultProps.isReactClassApproved && Re("getDefaultProps is only used on classic React.createClass definitions. Use a static property named `defaultProps` instead.");
        }
      }
      function Yn(h) {
        {
          for (var C = Object.keys(h.props), z = 0; z < C.length; z++) {
            var F = C[z];
            if (F !== "children" && F !== "key") {
              hi(h), Re("Invalid prop `%s` supplied to `React.Fragment`. React.Fragment can only have `key` and `children` props.", F), hi(null);
              break;
            }
          }
          h.ref !== null && (hi(h), Re("Invalid attribute `ref` supplied to `React.Fragment`."), hi(null));
        }
      }
      function Or(h, C, z) {
        var F = Y(h);
        if (!F) {
          var X = "";
          (h === void 0 || typeof h == "object" && h !== null && Object.keys(h).length === 0) && (X += " You likely forgot to export your component from the file it's defined in, or you might have mixed up default and named imports.");
          var Ne = mi(C);
          Ne ? X += Ne : X += Ju();
          var re;
          h === null ? re = "null" : Cn(h) ? re = "array" : h !== void 0 && h.$$typeof === Te ? (re = "<" + (Kn(h.type) || "Unknown") + " />", X = " Did you accidentally export a JSX literal instead of a component?") : re = typeof h, Re("React.createElement: type is invalid -- expected a string (for built-in components) or a class/function (for composite components) but got: %s.%s", re, X);
        }
        var Ae = ot.apply(this, arguments);
        if (Ae == null)
          return Ae;
        if (F)
          for (var mt = 2; mt < arguments.length; mt++)
            Qt(arguments[mt], h);
        return h === Ee ? Yn(Ae) : Sl(Ae), Ae;
      }
      var wa = !1;
      function iu(h) {
        var C = Or.bind(null, h);
        return C.type = h, wa || (wa = !0, Ot("React.createFactory() is deprecated and will be removed in a future major release. Consider using JSX or use React.createElement() directly instead.")), Object.defineProperty(C, "type", {
          enumerable: !1,
          get: function() {
            return Ot("Factory.type is deprecated. Access the class directly before passing it to createFactory."), Object.defineProperty(this, "type", {
              value: h
            }), h;
          }
        }), C;
      }
      function Wo(h, C, z) {
        for (var F = en.apply(this, arguments), X = 2; X < arguments.length; X++)
          Qt(arguments[X], F.type);
        return Sl(F), F;
      }
      function Go(h, C) {
        var z = it.transition;
        it.transition = {};
        var F = it.transition;
        it.transition._updatedFibers = /* @__PURE__ */ new Set();
        try {
          h();
        } finally {
          if (it.transition = z, z === null && F._updatedFibers) {
            var X = F._updatedFibers.size;
            X > 10 && Ot("Detected a large number of updates inside startTransition. If this is due to a subscription please re-write it to use React provided hooks. Otherwise concurrent mode guarantees are off the table."), F._updatedFibers.clear();
          }
        }
      }
      var El = !1, lu = null;
      function Wf(h) {
        if (lu === null)
          try {
            var C = ("require" + Math.random()).slice(0, 7), z = I && I[C];
            lu = z.call(I, "timers").setImmediate;
          } catch {
            lu = function(X) {
              El === !1 && (El = !0, typeof MessageChannel > "u" && Re("This browser does not have a MessageChannel implementation, so enqueuing tasks via await act(async () => ...) will fail. Please file an issue at https://github.com/facebook/react/issues if you encounter this warning."));
              var Ne = new MessageChannel();
              Ne.port1.onmessage = X, Ne.port2.postMessage(void 0);
            };
          }
        return lu(h);
      }
      var xa = 0, Ja = !1;
      function gi(h) {
        {
          var C = xa;
          xa++, ke.current === null && (ke.current = []);
          var z = ke.isBatchingLegacy, F;
          try {
            if (ke.isBatchingLegacy = !0, F = h(), !z && ke.didScheduleLegacyUpdate) {
              var X = ke.current;
              X !== null && (ke.didScheduleLegacyUpdate = !1, Cl(X));
            }
          } catch (st) {
            throw ba(C), st;
          } finally {
            ke.isBatchingLegacy = z;
          }
          if (F !== null && typeof F == "object" && typeof F.then == "function") {
            var Ne = F, re = !1, Ae = {
              then: function(st, Gt) {
                re = !0, Ne.then(function(hn) {
                  ba(C), xa === 0 ? eo(hn, st, Gt) : st(hn);
                }, function(hn) {
                  ba(C), Gt(hn);
                });
              }
            };
            return !Ja && typeof Promise < "u" && Promise.resolve().then(function() {
            }).then(function() {
              re || (Ja = !0, Re("You called act(async () => ...) without await. This could lead to unexpected testing behaviour, interleaving multiple act calls and mixing their scopes. You should - await act(async () => ...);"));
            }), Ae;
          } else {
            var mt = F;
            if (ba(C), xa === 0) {
              var bt = ke.current;
              bt !== null && (Cl(bt), ke.current = null);
              var rn = {
                then: function(st, Gt) {
                  ke.current === null ? (ke.current = [], eo(mt, st, Gt)) : st(mt);
                }
              };
              return rn;
            } else {
              var Wt = {
                then: function(st, Gt) {
                  st(mt);
                }
              };
              return Wt;
            }
          }
        }
      }
      function ba(h) {
        h !== xa - 1 && Re("You seem to have overlapping act() calls, this is not supported. Be sure to await previous act() calls before making a new one. "), xa = h;
      }
      function eo(h, C, z) {
        {
          var F = ke.current;
          if (F !== null)
            try {
              Cl(F), Wf(function() {
                F.length === 0 ? (ke.current = null, C(h)) : eo(h, C, z);
              });
            } catch (X) {
              z(X);
            }
          else
            C(h);
        }
      }
      var to = !1;
      function Cl(h) {
        if (!to) {
          to = !0;
          var C = 0;
          try {
            for (; C < h.length; C++) {
              var z = h[C];
              do
                z = z(!0);
              while (z !== null);
            }
            h.length = 0;
          } catch (F) {
            throw h = h.slice(C + 1), F;
          } finally {
            to = !1;
          }
        }
      }
      var uu = Or, no = Wo, ro = iu, ei = {
        map: Hi,
        forEach: eu,
        count: Jl,
        toArray: pl,
        only: vl
      };
      j.Children = ei, j.Component = Pe, j.Fragment = Ee, j.Profiler = Et, j.PureComponent = dt, j.StrictMode = S, j.Suspense = J, j.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = kt, j.act = gi, j.cloneElement = no, j.createContext = tu, j.createElement = uu, j.createFactory = ro, j.createRef = On, j.forwardRef = vi, j.isValidElement = vn, j.lazy = pi, j.memo = ie, j.startTransition = Go, j.unstable_act = gi, j.useCallback = ar, j.useContext = Ze, j.useDebugValue = Je, j.useDeferredValue = qa, j.useEffect = Tn, j.useId = nu, j.useImperativeHandle = Ka, j.useInsertionEffect = nn, j.useLayoutEffect = sn, j.useMemo = Ga, j.useReducer = ht, j.useRef = pt, j.useState = Ge, j.useSyncExternalStore = ru, j.useTransition = rt, j.version = k, typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop == "function" && __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop(new Error());
    }();
  }(Jp, Jp.exports)), Jp.exports;
}
process.env.NODE_ENV === "production" ? dE.exports = q_() : dE.exports = X_();
var Ya = dE.exports;
const Z_ = /* @__PURE__ */ K_(Ya);
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var XR;
function J_() {
  if (XR) return Xp;
  XR = 1;
  var I = Ya, j = Symbol.for("react.element"), k = Symbol.for("react.fragment"), Te = Object.prototype.hasOwnProperty, Fe = I.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ee = { key: !0, ref: !0, __self: !0, __source: !0 };
  function S(Et, se, ce) {
    var tt, J = {}, Se = null, ae = null;
    ce !== void 0 && (Se = "" + ce), se.key !== void 0 && (Se = "" + se.key), se.ref !== void 0 && (ae = se.ref);
    for (tt in se) Te.call(se, tt) && !Ee.hasOwnProperty(tt) && (J[tt] = se[tt]);
    if (Et && Et.defaultProps) for (tt in se = Et.defaultProps, se) J[tt] === void 0 && (J[tt] = se[tt]);
    return { $$typeof: j, type: Et, key: Se, ref: ae, props: J, _owner: Fe.current };
  }
  return Xp.Fragment = k, Xp.jsx = S, Xp.jsxs = S, Xp;
}
var Zp = {};
/**
 * @license React
 * react-jsx-runtime.development.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ZR;
function ek() {
  return ZR || (ZR = 1, process.env.NODE_ENV !== "production" && function() {
    var I = Ya, j = Symbol.for("react.element"), k = Symbol.for("react.portal"), Te = Symbol.for("react.fragment"), Fe = Symbol.for("react.strict_mode"), Ee = Symbol.for("react.profiler"), S = Symbol.for("react.provider"), Et = Symbol.for("react.context"), se = Symbol.for("react.forward_ref"), ce = Symbol.for("react.suspense"), tt = Symbol.for("react.suspense_list"), J = Symbol.for("react.memo"), Se = Symbol.for("react.lazy"), ae = Symbol.for("react.offscreen"), Ve = Symbol.iterator, at = "@@iterator";
    function ct(R) {
      if (R === null || typeof R != "object")
        return null;
      var Y = Ve && R[Ve] || R[at];
      return typeof Y == "function" ? Y : null;
    }
    var gt = I.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED;
    function qe(R) {
      {
        for (var Y = arguments.length, ie = new Array(Y > 1 ? Y - 1 : 0), he = 1; he < Y; he++)
          ie[he - 1] = arguments[he];
        Le("error", R, ie);
      }
    }
    function Le(R, Y, ie) {
      {
        var he = gt.ReactDebugCurrentFrame, Ze = he.getStackAddendum();
        Ze !== "" && (Y += "%s", ie = ie.concat([Ze]));
        var Ge = ie.map(function(ht) {
          return String(ht);
        });
        Ge.unshift("Warning: " + Y), Function.prototype.apply.call(console[R], console, Ge);
      }
    }
    var it = !1, ke = !1, Qe = !1, He = !1, ln = !1, Pt;
    Pt = Symbol.for("react.module.reference");
    function Jt(R) {
      return !!(typeof R == "string" || typeof R == "function" || R === Te || R === Ee || ln || R === Fe || R === ce || R === tt || He || R === ae || it || ke || Qe || typeof R == "object" && R !== null && (R.$$typeof === Se || R.$$typeof === J || R.$$typeof === S || R.$$typeof === Et || R.$$typeof === se || // This needs to include all possible module reference object
      // types supported by any Flight configuration anywhere since
      // we don't know which Flight build this will end up being used
      // with.
      R.$$typeof === Pt || R.getModuleId !== void 0));
    }
    function un(R, Y, ie) {
      var he = R.displayName;
      if (he)
        return he;
      var Ze = Y.displayName || Y.name || "";
      return Ze !== "" ? ie + "(" + Ze + ")" : ie;
    }
    function _t(R) {
      return R.displayName || "Context";
    }
    function Me(R) {
      if (R == null)
        return null;
      if (typeof R.tag == "number" && qe("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue."), typeof R == "function")
        return R.displayName || R.name || null;
      if (typeof R == "string")
        return R;
      switch (R) {
        case Te:
          return "Fragment";
        case k:
          return "Portal";
        case Ee:
          return "Profiler";
        case Fe:
          return "StrictMode";
        case ce:
          return "Suspense";
        case tt:
          return "SuspenseList";
      }
      if (typeof R == "object")
        switch (R.$$typeof) {
          case Et:
            var Y = R;
            return _t(Y) + ".Consumer";
          case S:
            var ie = R;
            return _t(ie._context) + ".Provider";
          case se:
            return un(R, R.render, "ForwardRef");
          case J:
            var he = R.displayName || null;
            return he !== null ? he : Me(R.type) || "Memo";
          case Se: {
            var Ze = R, Ge = Ze._payload, ht = Ze._init;
            try {
              return Me(ht(Ge));
            } catch {
              return null;
            }
          }
        }
      return null;
    }
    var Ft = Object.assign, kt = 0, Ot, Re, Z, we, ne, _, V;
    function Ie() {
    }
    Ie.__reactDisabledLog = !0;
    function Pe() {
      {
        if (kt === 0) {
          Ot = console.log, Re = console.info, Z = console.warn, we = console.error, ne = console.group, _ = console.groupCollapsed, V = console.groupEnd;
          var R = {
            configurable: !0,
            enumerable: !0,
            value: Ie,
            writable: !0
          };
          Object.defineProperties(console, {
            info: R,
            log: R,
            warn: R,
            error: R,
            group: R,
            groupCollapsed: R,
            groupEnd: R
          });
        }
        kt++;
      }
    }
    function ft() {
      {
        if (kt--, kt === 0) {
          var R = {
            configurable: !0,
            enumerable: !0,
            writable: !0
          };
          Object.defineProperties(console, {
            log: Ft({}, R, {
              value: Ot
            }),
            info: Ft({}, R, {
              value: Re
            }),
            warn: Ft({}, R, {
              value: Z
            }),
            error: Ft({}, R, {
              value: we
            }),
            group: Ft({}, R, {
              value: ne
            }),
            groupCollapsed: Ft({}, R, {
              value: _
            }),
            groupEnd: Ft({}, R, {
              value: V
            })
          });
        }
        kt < 0 && qe("disabledDepth fell below zero. This is a bug in React. Please file an issue.");
      }
    }
    var lt = gt.ReactCurrentDispatcher, nt;
    function ut(R, Y, ie) {
      {
        if (nt === void 0)
          try {
            throw Error();
          } catch (Ze) {
            var he = Ze.stack.trim().match(/\n( *(at )?)/);
            nt = he && he[1] || "";
          }
        return `
` + nt + R;
      }
    }
    var dt = !1, It;
    {
      var On = typeof WeakMap == "function" ? WeakMap : Map;
      It = new On();
    }
    function xr(R, Y) {
      if (!R || dt)
        return "";
      {
        var ie = It.get(R);
        if (ie !== void 0)
          return ie;
      }
      var he;
      dt = !0;
      var Ze = Error.prepareStackTrace;
      Error.prepareStackTrace = void 0;
      var Ge;
      Ge = lt.current, lt.current = null, Pe();
      try {
        if (Y) {
          var ht = function() {
            throw Error();
          };
          if (Object.defineProperty(ht.prototype, "props", {
            set: function() {
              throw Error();
            }
          }), typeof Reflect == "object" && Reflect.construct) {
            try {
              Reflect.construct(ht, []);
            } catch (Je) {
              he = Je;
            }
            Reflect.construct(R, [], ht);
          } else {
            try {
              ht.call();
            } catch (Je) {
              he = Je;
            }
            R.call(ht.prototype);
          }
        } else {
          try {
            throw Error();
          } catch (Je) {
            he = Je;
          }
          R();
        }
      } catch (Je) {
        if (Je && he && typeof Je.stack == "string") {
          for (var pt = Je.stack.split(`
`), Tn = he.stack.split(`
`), nn = pt.length - 1, sn = Tn.length - 1; nn >= 1 && sn >= 0 && pt[nn] !== Tn[sn]; )
            sn--;
          for (; nn >= 1 && sn >= 0; nn--, sn--)
            if (pt[nn] !== Tn[sn]) {
              if (nn !== 1 || sn !== 1)
                do
                  if (nn--, sn--, sn < 0 || pt[nn] !== Tn[sn]) {
                    var ar = `
` + pt[nn].replace(" at new ", " at ");
                    return R.displayName && ar.includes("<anonymous>") && (ar = ar.replace("<anonymous>", R.displayName)), typeof R == "function" && It.set(R, ar), ar;
                  }
                while (nn >= 1 && sn >= 0);
              break;
            }
        }
      } finally {
        dt = !1, lt.current = Ge, ft(), Error.prepareStackTrace = Ze;
      }
      var Ga = R ? R.displayName || R.name : "", Ka = Ga ? ut(Ga) : "";
      return typeof R == "function" && It.set(R, Ka), Ka;
    }
    function Cn(R, Y, ie) {
      return xr(R, !1);
    }
    function nr(R) {
      var Y = R.prototype;
      return !!(Y && Y.isReactComponent);
    }
    function Vn(R, Y, ie) {
      if (R == null)
        return "";
      if (typeof R == "function")
        return xr(R, nr(R));
      if (typeof R == "string")
        return ut(R);
      switch (R) {
        case ce:
          return ut("Suspense");
        case tt:
          return ut("SuspenseList");
      }
      if (typeof R == "object")
        switch (R.$$typeof) {
          case se:
            return Cn(R.render);
          case J:
            return Vn(R.type, Y, ie);
          case Se: {
            var he = R, Ze = he._payload, Ge = he._init;
            try {
              return Vn(Ge(Ze), Y, ie);
            } catch {
            }
          }
        }
      return "";
    }
    var Bn = Object.prototype.hasOwnProperty, Yr = {}, ci = gt.ReactDebugCurrentFrame;
    function oa(R) {
      if (R) {
        var Y = R._owner, ie = Vn(R.type, R._source, Y ? Y.type : null);
        ci.setExtraStackFrame(ie);
      } else
        ci.setExtraStackFrame(null);
    }
    function Kn(R, Y, ie, he, Ze) {
      {
        var Ge = Function.call.bind(Bn);
        for (var ht in R)
          if (Ge(R, ht)) {
            var pt = void 0;
            try {
              if (typeof R[ht] != "function") {
                var Tn = Error((he || "React class") + ": " + ie + " type `" + ht + "` is invalid; it must be a function, usually from the `prop-types` package, but received `" + typeof R[ht] + "`.This often happens because of typos such as `PropTypes.function` instead of `PropTypes.func`.");
                throw Tn.name = "Invariant Violation", Tn;
              }
              pt = R[ht](Y, ht, he, ie, null, "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED");
            } catch (nn) {
              pt = nn;
            }
            pt && !(pt instanceof Error) && (oa(Ze), qe("%s: type specification of %s `%s` is invalid; the type checker function must return `null` or an `Error` but returned a %s. You may have forgotten to pass an argument to the type checker creator (arrayOf, instanceOf, objectOf, oneOf, oneOfType, and shape all require an argument).", he || "React class", ie, ht, typeof pt), oa(null)), pt instanceof Error && !(pt.message in Yr) && (Yr[pt.message] = !0, oa(Ze), qe("Failed %s type: %s", ie, pt.message), oa(null));
          }
      }
    }
    var Rn = Array.isArray;
    function In(R) {
      return Rn(R);
    }
    function gr(R) {
      {
        var Y = typeof Symbol == "function" && Symbol.toStringTag, ie = Y && R[Symbol.toStringTag] || R.constructor.name || "Object";
        return ie;
      }
    }
    function $a(R) {
      try {
        return Ln(R), !1;
      } catch {
        return !0;
      }
    }
    function Ln(R) {
      return "" + R;
    }
    function Sr(R) {
      if ($a(R))
        return qe("The provided key is an unsupported type %s. This value must be coerced to a string before before using it here.", gr(R)), Ln(R);
    }
    var sa = gt.ReactCurrentOwner, Qa = {
      key: !0,
      ref: !0,
      __self: !0,
      __source: !0
    }, fi, ee;
    function xe(R) {
      if (Bn.call(R, "ref")) {
        var Y = Object.getOwnPropertyDescriptor(R, "ref").get;
        if (Y && Y.isReactWarning)
          return !1;
      }
      return R.ref !== void 0;
    }
    function ot(R) {
      if (Bn.call(R, "key")) {
        var Y = Object.getOwnPropertyDescriptor(R, "key").get;
        if (Y && Y.isReactWarning)
          return !1;
      }
      return R.key !== void 0;
    }
    function Ht(R, Y) {
      typeof R.ref == "string" && sa.current;
    }
    function en(R, Y) {
      {
        var ie = function() {
          fi || (fi = !0, qe("%s: `key` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://reactjs.org/link/special-props)", Y));
        };
        ie.isReactWarning = !0, Object.defineProperty(R, "key", {
          get: ie,
          configurable: !0
        });
      }
    }
    function vn(R, Y) {
      {
        var ie = function() {
          ee || (ee = !0, qe("%s: `ref` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://reactjs.org/link/special-props)", Y));
        };
        ie.isReactWarning = !0, Object.defineProperty(R, "ref", {
          get: ie,
          configurable: !0
        });
      }
    }
    var on = function(R, Y, ie, he, Ze, Ge, ht) {
      var pt = {
        // This tag allows us to uniquely identify this as a React Element
        $$typeof: j,
        // Built-in properties that belong on the element
        type: R,
        key: Y,
        ref: ie,
        props: ht,
        // Record the component responsible for creating this element.
        _owner: Ge
      };
      return pt._store = {}, Object.defineProperty(pt._store, "validated", {
        configurable: !1,
        enumerable: !1,
        writable: !0,
        value: !1
      }), Object.defineProperty(pt, "_self", {
        configurable: !1,
        enumerable: !1,
        writable: !1,
        value: he
      }), Object.defineProperty(pt, "_source", {
        configurable: !1,
        enumerable: !1,
        writable: !1,
        value: Ze
      }), Object.freeze && (Object.freeze(pt.props), Object.freeze(pt)), pt;
    };
    function qn(R, Y, ie, he, Ze) {
      {
        var Ge, ht = {}, pt = null, Tn = null;
        ie !== void 0 && (Sr(ie), pt = "" + ie), ot(Y) && (Sr(Y.key), pt = "" + Y.key), xe(Y) && (Tn = Y.ref, Ht(Y, Ze));
        for (Ge in Y)
          Bn.call(Y, Ge) && !Qa.hasOwnProperty(Ge) && (ht[Ge] = Y[Ge]);
        if (R && R.defaultProps) {
          var nn = R.defaultProps;
          for (Ge in nn)
            ht[Ge] === void 0 && (ht[Ge] = nn[Ge]);
        }
        if (pt || Tn) {
          var sn = typeof R == "function" ? R.displayName || R.name || "Unknown" : R;
          pt && en(ht, sn), Tn && vn(ht, sn);
        }
        return on(R, pt, Tn, Ze, he, sa.current, ht);
      }
    }
    var tn = gt.ReactCurrentOwner, Yt = gt.ReactDebugCurrentFrame;
    function $t(R) {
      if (R) {
        var Y = R._owner, ie = Vn(R.type, R._source, Y ? Y.type : null);
        Yt.setExtraStackFrame(ie);
      } else
        Yt.setExtraStackFrame(null);
    }
    var ca;
    ca = !1;
    function Er(R) {
      return typeof R == "object" && R !== null && R.$$typeof === j;
    }
    function Ta() {
      {
        if (tn.current) {
          var R = Me(tn.current.type);
          if (R)
            return `

Check the render method of \`` + R + "`.";
        }
        return "";
      }
    }
    function Hi(R) {
      return "";
    }
    var Jl = {};
    function eu(R) {
      {
        var Y = Ta();
        if (!Y) {
          var ie = typeof R == "string" ? R : R.displayName || R.name;
          ie && (Y = `

Check the top-level render call using <` + ie + ">.");
        }
        return Y;
      }
    }
    function pl(R, Y) {
      {
        if (!R._store || R._store.validated || R.key != null)
          return;
        R._store.validated = !0;
        var ie = eu(Y);
        if (Jl[ie])
          return;
        Jl[ie] = !0;
        var he = "";
        R && R._owner && R._owner !== tn.current && (he = " It was passed a child from " + Me(R._owner.type) + "."), $t(R), qe('Each child in a list should have a unique "key" prop.%s%s See https://reactjs.org/link/warning-keys for more information.', ie, he), $t(null);
      }
    }
    function vl(R, Y) {
      {
        if (typeof R != "object")
          return;
        if (In(R))
          for (var ie = 0; ie < R.length; ie++) {
            var he = R[ie];
            Er(he) && pl(he, Y);
          }
        else if (Er(R))
          R._store && (R._store.validated = !0);
        else if (R) {
          var Ze = ct(R);
          if (typeof Ze == "function" && Ze !== R.entries)
            for (var Ge = Ze.call(R), ht; !(ht = Ge.next()).done; )
              Er(ht.value) && pl(ht.value, Y);
        }
      }
    }
    function tu(R) {
      {
        var Y = R.type;
        if (Y == null || typeof Y == "string")
          return;
        var ie;
        if (typeof Y == "function")
          ie = Y.propTypes;
        else if (typeof Y == "object" && (Y.$$typeof === se || // Note: Memo only checks outer props here.
        // Inner props are checked in the reconciler.
        Y.$$typeof === J))
          ie = Y.propTypes;
        else
          return;
        if (ie) {
          var he = Me(Y);
          Kn(ie, R.props, "prop", he, R);
        } else if (Y.PropTypes !== void 0 && !ca) {
          ca = !0;
          var Ze = Me(Y);
          qe("Component %s declared `PropTypes` instead of `propTypes`. Did you misspell the property assignment?", Ze || "Unknown");
        }
        typeof Y.getDefaultProps == "function" && !Y.getDefaultProps.isReactClassApproved && qe("getDefaultProps is only used on classic React.createClass definitions. Use a static property named `defaultProps` instead.");
      }
    }
    function br(R) {
      {
        for (var Y = Object.keys(R.props), ie = 0; ie < Y.length; ie++) {
          var he = Y[ie];
          if (he !== "children" && he !== "key") {
            $t(R), qe("Invalid prop `%s` supplied to `React.Fragment`. React.Fragment can only have `key` and `children` props.", he), $t(null);
            break;
          }
        }
        R.ref !== null && ($t(R), qe("Invalid attribute `ref` supplied to `React.Fragment`."), $t(null));
      }
    }
    var _r = {};
    function rr(R, Y, ie, he, Ze, Ge) {
      {
        var ht = Jt(R);
        if (!ht) {
          var pt = "";
          (R === void 0 || typeof R == "object" && R !== null && Object.keys(R).length === 0) && (pt += " You likely forgot to export your component from the file it's defined in, or you might have mixed up default and named imports.");
          var Tn = Hi();
          Tn ? pt += Tn : pt += Ta();
          var nn;
          R === null ? nn = "null" : In(R) ? nn = "array" : R !== void 0 && R.$$typeof === j ? (nn = "<" + (Me(R.type) || "Unknown") + " />", pt = " Did you accidentally export a JSX literal instead of a component?") : nn = typeof R, qe("React.jsx: type is invalid -- expected a string (for built-in components) or a class/function (for composite components) but got: %s.%s", nn, pt);
        }
        var sn = qn(R, Y, ie, Ze, Ge);
        if (sn == null)
          return sn;
        if (ht) {
          var ar = Y.children;
          if (ar !== void 0)
            if (he)
              if (In(ar)) {
                for (var Ga = 0; Ga < ar.length; Ga++)
                  vl(ar[Ga], R);
                Object.freeze && Object.freeze(ar);
              } else
                qe("React.jsx: Static children should always be an array. You are likely explicitly calling React.jsxs or React.jsxDEV. Use the Babel transform instead.");
            else
              vl(ar, R);
        }
        if (Bn.call(Y, "key")) {
          var Ka = Me(R), Je = Object.keys(Y).filter(function(nu) {
            return nu !== "key";
          }), rt = Je.length > 0 ? "{key: someKey, " + Je.join(": ..., ") + ": ...}" : "{key: someKey}";
          if (!_r[Ka + rt]) {
            var qa = Je.length > 0 ? "{" + Je.join(": ..., ") + ": ...}" : "{}";
            qe(`A props object containing a "key" prop is being spread into JSX:
  let props = %s;
  <%s {...props} />
React keys must be passed directly to JSX without using spread:
  let props = %s;
  <%s key={someKey} {...props} />`, rt, Ka, qa, Ka), _r[Ka + rt] = !0;
          }
        }
        return R === Te ? br(sn) : tu(sn), sn;
      }
    }
    function di(R, Y, ie) {
      return rr(R, Y, ie, !0);
    }
    function Wa(R, Y, ie) {
      return rr(R, Y, ie, !1);
    }
    var pi = Wa, vi = di;
    Zp.Fragment = Te, Zp.jsx = pi, Zp.jsxs = vi;
  }()), Zp;
}
process.env.NODE_ENV === "production" ? fE.exports = J_() : fE.exports = ek();
var jt = fE.exports, pE = { exports: {} }, Ba = {}, $m = { exports: {} }, sE = {};
/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var JR;
function tk() {
  return JR || (JR = 1, function(I) {
    function j(Z, we) {
      var ne = Z.length;
      Z.push(we);
      e: for (; 0 < ne; ) {
        var _ = ne - 1 >>> 1, V = Z[_];
        if (0 < Fe(V, we)) Z[_] = we, Z[ne] = V, ne = _;
        else break e;
      }
    }
    function k(Z) {
      return Z.length === 0 ? null : Z[0];
    }
    function Te(Z) {
      if (Z.length === 0) return null;
      var we = Z[0], ne = Z.pop();
      if (ne !== we) {
        Z[0] = ne;
        e: for (var _ = 0, V = Z.length, Ie = V >>> 1; _ < Ie; ) {
          var Pe = 2 * (_ + 1) - 1, ft = Z[Pe], lt = Pe + 1, nt = Z[lt];
          if (0 > Fe(ft, ne)) lt < V && 0 > Fe(nt, ft) ? (Z[_] = nt, Z[lt] = ne, _ = lt) : (Z[_] = ft, Z[Pe] = ne, _ = Pe);
          else if (lt < V && 0 > Fe(nt, ne)) Z[_] = nt, Z[lt] = ne, _ = lt;
          else break e;
        }
      }
      return we;
    }
    function Fe(Z, we) {
      var ne = Z.sortIndex - we.sortIndex;
      return ne !== 0 ? ne : Z.id - we.id;
    }
    if (typeof performance == "object" && typeof performance.now == "function") {
      var Ee = performance;
      I.unstable_now = function() {
        return Ee.now();
      };
    } else {
      var S = Date, Et = S.now();
      I.unstable_now = function() {
        return S.now() - Et;
      };
    }
    var se = [], ce = [], tt = 1, J = null, Se = 3, ae = !1, Ve = !1, at = !1, ct = typeof setTimeout == "function" ? setTimeout : null, gt = typeof clearTimeout == "function" ? clearTimeout : null, qe = typeof setImmediate < "u" ? setImmediate : null;
    typeof navigator < "u" && navigator.scheduling !== void 0 && navigator.scheduling.isInputPending !== void 0 && navigator.scheduling.isInputPending.bind(navigator.scheduling);
    function Le(Z) {
      for (var we = k(ce); we !== null; ) {
        if (we.callback === null) Te(ce);
        else if (we.startTime <= Z) Te(ce), we.sortIndex = we.expirationTime, j(se, we);
        else break;
        we = k(ce);
      }
    }
    function it(Z) {
      if (at = !1, Le(Z), !Ve) if (k(se) !== null) Ve = !0, Ot(ke);
      else {
        var we = k(ce);
        we !== null && Re(it, we.startTime - Z);
      }
    }
    function ke(Z, we) {
      Ve = !1, at && (at = !1, gt(ln), ln = -1), ae = !0;
      var ne = Se;
      try {
        for (Le(we), J = k(se); J !== null && (!(J.expirationTime > we) || Z && !un()); ) {
          var _ = J.callback;
          if (typeof _ == "function") {
            J.callback = null, Se = J.priorityLevel;
            var V = _(J.expirationTime <= we);
            we = I.unstable_now(), typeof V == "function" ? J.callback = V : J === k(se) && Te(se), Le(we);
          } else Te(se);
          J = k(se);
        }
        if (J !== null) var Ie = !0;
        else {
          var Pe = k(ce);
          Pe !== null && Re(it, Pe.startTime - we), Ie = !1;
        }
        return Ie;
      } finally {
        J = null, Se = ne, ae = !1;
      }
    }
    var Qe = !1, He = null, ln = -1, Pt = 5, Jt = -1;
    function un() {
      return !(I.unstable_now() - Jt < Pt);
    }
    function _t() {
      if (He !== null) {
        var Z = I.unstable_now();
        Jt = Z;
        var we = !0;
        try {
          we = He(!0, Z);
        } finally {
          we ? Me() : (Qe = !1, He = null);
        }
      } else Qe = !1;
    }
    var Me;
    if (typeof qe == "function") Me = function() {
      qe(_t);
    };
    else if (typeof MessageChannel < "u") {
      var Ft = new MessageChannel(), kt = Ft.port2;
      Ft.port1.onmessage = _t, Me = function() {
        kt.postMessage(null);
      };
    } else Me = function() {
      ct(_t, 0);
    };
    function Ot(Z) {
      He = Z, Qe || (Qe = !0, Me());
    }
    function Re(Z, we) {
      ln = ct(function() {
        Z(I.unstable_now());
      }, we);
    }
    I.unstable_IdlePriority = 5, I.unstable_ImmediatePriority = 1, I.unstable_LowPriority = 4, I.unstable_NormalPriority = 3, I.unstable_Profiling = null, I.unstable_UserBlockingPriority = 2, I.unstable_cancelCallback = function(Z) {
      Z.callback = null;
    }, I.unstable_continueExecution = function() {
      Ve || ae || (Ve = !0, Ot(ke));
    }, I.unstable_forceFrameRate = function(Z) {
      0 > Z || 125 < Z ? console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported") : Pt = 0 < Z ? Math.floor(1e3 / Z) : 5;
    }, I.unstable_getCurrentPriorityLevel = function() {
      return Se;
    }, I.unstable_getFirstCallbackNode = function() {
      return k(se);
    }, I.unstable_next = function(Z) {
      switch (Se) {
        case 1:
        case 2:
        case 3:
          var we = 3;
          break;
        default:
          we = Se;
      }
      var ne = Se;
      Se = we;
      try {
        return Z();
      } finally {
        Se = ne;
      }
    }, I.unstable_pauseExecution = function() {
    }, I.unstable_requestPaint = function() {
    }, I.unstable_runWithPriority = function(Z, we) {
      switch (Z) {
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
          break;
        default:
          Z = 3;
      }
      var ne = Se;
      Se = Z;
      try {
        return we();
      } finally {
        Se = ne;
      }
    }, I.unstable_scheduleCallback = function(Z, we, ne) {
      var _ = I.unstable_now();
      switch (typeof ne == "object" && ne !== null ? (ne = ne.delay, ne = typeof ne == "number" && 0 < ne ? _ + ne : _) : ne = _, Z) {
        case 1:
          var V = -1;
          break;
        case 2:
          V = 250;
          break;
        case 5:
          V = 1073741823;
          break;
        case 4:
          V = 1e4;
          break;
        default:
          V = 5e3;
      }
      return V = ne + V, Z = { id: tt++, callback: we, priorityLevel: Z, startTime: ne, expirationTime: V, sortIndex: -1 }, ne > _ ? (Z.sortIndex = ne, j(ce, Z), k(se) === null && Z === k(ce) && (at ? (gt(ln), ln = -1) : at = !0, Re(it, ne - _))) : (Z.sortIndex = V, j(se, Z), Ve || ae || (Ve = !0, Ot(ke))), Z;
    }, I.unstable_shouldYield = un, I.unstable_wrapCallback = function(Z) {
      var we = Se;
      return function() {
        var ne = Se;
        Se = we;
        try {
          return Z.apply(this, arguments);
        } finally {
          Se = ne;
        }
      };
    };
  }(sE)), sE;
}
var cE = {};
/**
 * @license React
 * scheduler.development.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var eT;
function nk() {
  return eT || (eT = 1, function(I) {
    process.env.NODE_ENV !== "production" && function() {
      typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart == "function" && __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart(new Error());
      var j = !1, k = 5;
      function Te(ee, xe) {
        var ot = ee.length;
        ee.push(xe), S(ee, xe, ot);
      }
      function Fe(ee) {
        return ee.length === 0 ? null : ee[0];
      }
      function Ee(ee) {
        if (ee.length === 0)
          return null;
        var xe = ee[0], ot = ee.pop();
        return ot !== xe && (ee[0] = ot, Et(ee, ot, 0)), xe;
      }
      function S(ee, xe, ot) {
        for (var Ht = ot; Ht > 0; ) {
          var en = Ht - 1 >>> 1, vn = ee[en];
          if (se(vn, xe) > 0)
            ee[en] = xe, ee[Ht] = vn, Ht = en;
          else
            return;
        }
      }
      function Et(ee, xe, ot) {
        for (var Ht = ot, en = ee.length, vn = en >>> 1; Ht < vn; ) {
          var on = (Ht + 1) * 2 - 1, qn = ee[on], tn = on + 1, Yt = ee[tn];
          if (se(qn, xe) < 0)
            tn < en && se(Yt, qn) < 0 ? (ee[Ht] = Yt, ee[tn] = xe, Ht = tn) : (ee[Ht] = qn, ee[on] = xe, Ht = on);
          else if (tn < en && se(Yt, xe) < 0)
            ee[Ht] = Yt, ee[tn] = xe, Ht = tn;
          else
            return;
        }
      }
      function se(ee, xe) {
        var ot = ee.sortIndex - xe.sortIndex;
        return ot !== 0 ? ot : ee.id - xe.id;
      }
      var ce = 1, tt = 2, J = 3, Se = 4, ae = 5;
      function Ve(ee, xe) {
      }
      var at = typeof performance == "object" && typeof performance.now == "function";
      if (at) {
        var ct = performance;
        I.unstable_now = function() {
          return ct.now();
        };
      } else {
        var gt = Date, qe = gt.now();
        I.unstable_now = function() {
          return gt.now() - qe;
        };
      }
      var Le = 1073741823, it = -1, ke = 250, Qe = 5e3, He = 1e4, ln = Le, Pt = [], Jt = [], un = 1, _t = null, Me = J, Ft = !1, kt = !1, Ot = !1, Re = typeof setTimeout == "function" ? setTimeout : null, Z = typeof clearTimeout == "function" ? clearTimeout : null, we = typeof setImmediate < "u" ? setImmediate : null;
      typeof navigator < "u" && navigator.scheduling !== void 0 && navigator.scheduling.isInputPending !== void 0 && navigator.scheduling.isInputPending.bind(navigator.scheduling);
      function ne(ee) {
        for (var xe = Fe(Jt); xe !== null; ) {
          if (xe.callback === null)
            Ee(Jt);
          else if (xe.startTime <= ee)
            Ee(Jt), xe.sortIndex = xe.expirationTime, Te(Pt, xe);
          else
            return;
          xe = Fe(Jt);
        }
      }
      function _(ee) {
        if (Ot = !1, ne(ee), !kt)
          if (Fe(Pt) !== null)
            kt = !0, Ln(V);
          else {
            var xe = Fe(Jt);
            xe !== null && Sr(_, xe.startTime - ee);
          }
      }
      function V(ee, xe) {
        kt = !1, Ot && (Ot = !1, sa()), Ft = !0;
        var ot = Me;
        try {
          var Ht;
          if (!j) return Ie(ee, xe);
        } finally {
          _t = null, Me = ot, Ft = !1;
        }
      }
      function Ie(ee, xe) {
        var ot = xe;
        for (ne(ot), _t = Fe(Pt); _t !== null && !(_t.expirationTime > ot && (!ee || ci())); ) {
          var Ht = _t.callback;
          if (typeof Ht == "function") {
            _t.callback = null, Me = _t.priorityLevel;
            var en = _t.expirationTime <= ot, vn = Ht(en);
            ot = I.unstable_now(), typeof vn == "function" ? _t.callback = vn : _t === Fe(Pt) && Ee(Pt), ne(ot);
          } else
            Ee(Pt);
          _t = Fe(Pt);
        }
        if (_t !== null)
          return !0;
        var on = Fe(Jt);
        return on !== null && Sr(_, on.startTime - ot), !1;
      }
      function Pe(ee, xe) {
        switch (ee) {
          case ce:
          case tt:
          case J:
          case Se:
          case ae:
            break;
          default:
            ee = J;
        }
        var ot = Me;
        Me = ee;
        try {
          return xe();
        } finally {
          Me = ot;
        }
      }
      function ft(ee) {
        var xe;
        switch (Me) {
          case ce:
          case tt:
          case J:
            xe = J;
            break;
          default:
            xe = Me;
            break;
        }
        var ot = Me;
        Me = xe;
        try {
          return ee();
        } finally {
          Me = ot;
        }
      }
      function lt(ee) {
        var xe = Me;
        return function() {
          var ot = Me;
          Me = xe;
          try {
            return ee.apply(this, arguments);
          } finally {
            Me = ot;
          }
        };
      }
      function nt(ee, xe, ot) {
        var Ht = I.unstable_now(), en;
        if (typeof ot == "object" && ot !== null) {
          var vn = ot.delay;
          typeof vn == "number" && vn > 0 ? en = Ht + vn : en = Ht;
        } else
          en = Ht;
        var on;
        switch (ee) {
          case ce:
            on = it;
            break;
          case tt:
            on = ke;
            break;
          case ae:
            on = ln;
            break;
          case Se:
            on = He;
            break;
          case J:
          default:
            on = Qe;
            break;
        }
        var qn = en + on, tn = {
          id: un++,
          callback: xe,
          priorityLevel: ee,
          startTime: en,
          expirationTime: qn,
          sortIndex: -1
        };
        return en > Ht ? (tn.sortIndex = en, Te(Jt, tn), Fe(Pt) === null && tn === Fe(Jt) && (Ot ? sa() : Ot = !0, Sr(_, en - Ht))) : (tn.sortIndex = qn, Te(Pt, tn), !kt && !Ft && (kt = !0, Ln(V))), tn;
      }
      function ut() {
      }
      function dt() {
        !kt && !Ft && (kt = !0, Ln(V));
      }
      function It() {
        return Fe(Pt);
      }
      function On(ee) {
        ee.callback = null;
      }
      function xr() {
        return Me;
      }
      var Cn = !1, nr = null, Vn = -1, Bn = k, Yr = -1;
      function ci() {
        var ee = I.unstable_now() - Yr;
        return !(ee < Bn);
      }
      function oa() {
      }
      function Kn(ee) {
        if (ee < 0 || ee > 125) {
          console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported");
          return;
        }
        ee > 0 ? Bn = Math.floor(1e3 / ee) : Bn = k;
      }
      var Rn = function() {
        if (nr !== null) {
          var ee = I.unstable_now();
          Yr = ee;
          var xe = !0, ot = !0;
          try {
            ot = nr(xe, ee);
          } finally {
            ot ? In() : (Cn = !1, nr = null);
          }
        } else
          Cn = !1;
      }, In;
      if (typeof we == "function")
        In = function() {
          we(Rn);
        };
      else if (typeof MessageChannel < "u") {
        var gr = new MessageChannel(), $a = gr.port2;
        gr.port1.onmessage = Rn, In = function() {
          $a.postMessage(null);
        };
      } else
        In = function() {
          Re(Rn, 0);
        };
      function Ln(ee) {
        nr = ee, Cn || (Cn = !0, In());
      }
      function Sr(ee, xe) {
        Vn = Re(function() {
          ee(I.unstable_now());
        }, xe);
      }
      function sa() {
        Z(Vn), Vn = -1;
      }
      var Qa = oa, fi = null;
      I.unstable_IdlePriority = ae, I.unstable_ImmediatePriority = ce, I.unstable_LowPriority = Se, I.unstable_NormalPriority = J, I.unstable_Profiling = fi, I.unstable_UserBlockingPriority = tt, I.unstable_cancelCallback = On, I.unstable_continueExecution = dt, I.unstable_forceFrameRate = Kn, I.unstable_getCurrentPriorityLevel = xr, I.unstable_getFirstCallbackNode = It, I.unstable_next = ft, I.unstable_pauseExecution = ut, I.unstable_requestPaint = Qa, I.unstable_runWithPriority = Pe, I.unstable_scheduleCallback = nt, I.unstable_shouldYield = ci, I.unstable_wrapCallback = lt, typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop == "function" && __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop(new Error());
    }();
  }(cE)), cE;
}
var tT;
function lT() {
  return tT || (tT = 1, process.env.NODE_ENV === "production" ? $m.exports = tk() : $m.exports = nk()), $m.exports;
}
/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var nT;
function rk() {
  if (nT) return Ba;
  nT = 1;
  var I = Ya, j = lT();
  function k(n) {
    for (var r = "https://reactjs.org/docs/error-decoder.html?invariant=" + n, l = 1; l < arguments.length; l++) r += "&args[]=" + encodeURIComponent(arguments[l]);
    return "Minified React error #" + n + "; visit " + r + " for the full message or use the non-minified dev environment for full errors and additional helpful warnings.";
  }
  var Te = /* @__PURE__ */ new Set(), Fe = {};
  function Ee(n, r) {
    S(n, r), S(n + "Capture", r);
  }
  function S(n, r) {
    for (Fe[n] = r, n = 0; n < r.length; n++) Te.add(r[n]);
  }
  var Et = !(typeof window > "u" || typeof window.document > "u" || typeof window.document.createElement > "u"), se = Object.prototype.hasOwnProperty, ce = /^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/, tt = {}, J = {};
  function Se(n) {
    return se.call(J, n) ? !0 : se.call(tt, n) ? !1 : ce.test(n) ? J[n] = !0 : (tt[n] = !0, !1);
  }
  function ae(n, r, l, o) {
    if (l !== null && l.type === 0) return !1;
    switch (typeof r) {
      case "function":
      case "symbol":
        return !0;
      case "boolean":
        return o ? !1 : l !== null ? !l.acceptsBooleans : (n = n.toLowerCase().slice(0, 5), n !== "data-" && n !== "aria-");
      default:
        return !1;
    }
  }
  function Ve(n, r, l, o) {
    if (r === null || typeof r > "u" || ae(n, r, l, o)) return !0;
    if (o) return !1;
    if (l !== null) switch (l.type) {
      case 3:
        return !r;
      case 4:
        return r === !1;
      case 5:
        return isNaN(r);
      case 6:
        return isNaN(r) || 1 > r;
    }
    return !1;
  }
  function at(n, r, l, o, c, d, m) {
    this.acceptsBooleans = r === 2 || r === 3 || r === 4, this.attributeName = o, this.attributeNamespace = c, this.mustUseProperty = l, this.propertyName = n, this.type = r, this.sanitizeURL = d, this.removeEmptyString = m;
  }
  var ct = {};
  "children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(n) {
    ct[n] = new at(n, 0, !1, n, null, !1, !1);
  }), [["acceptCharset", "accept-charset"], ["className", "class"], ["htmlFor", "for"], ["httpEquiv", "http-equiv"]].forEach(function(n) {
    var r = n[0];
    ct[r] = new at(r, 1, !1, n[1], null, !1, !1);
  }), ["contentEditable", "draggable", "spellCheck", "value"].forEach(function(n) {
    ct[n] = new at(n, 2, !1, n.toLowerCase(), null, !1, !1);
  }), ["autoReverse", "externalResourcesRequired", "focusable", "preserveAlpha"].forEach(function(n) {
    ct[n] = new at(n, 2, !1, n, null, !1, !1);
  }), "allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(n) {
    ct[n] = new at(n, 3, !1, n.toLowerCase(), null, !1, !1);
  }), ["checked", "multiple", "muted", "selected"].forEach(function(n) {
    ct[n] = new at(n, 3, !0, n, null, !1, !1);
  }), ["capture", "download"].forEach(function(n) {
    ct[n] = new at(n, 4, !1, n, null, !1, !1);
  }), ["cols", "rows", "size", "span"].forEach(function(n) {
    ct[n] = new at(n, 6, !1, n, null, !1, !1);
  }), ["rowSpan", "start"].forEach(function(n) {
    ct[n] = new at(n, 5, !1, n.toLowerCase(), null, !1, !1);
  });
  var gt = /[\-:]([a-z])/g;
  function qe(n) {
    return n[1].toUpperCase();
  }
  "accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(n) {
    var r = n.replace(
      gt,
      qe
    );
    ct[r] = new at(r, 1, !1, n, null, !1, !1);
  }), "xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(n) {
    var r = n.replace(gt, qe);
    ct[r] = new at(r, 1, !1, n, "http://www.w3.org/1999/xlink", !1, !1);
  }), ["xml:base", "xml:lang", "xml:space"].forEach(function(n) {
    var r = n.replace(gt, qe);
    ct[r] = new at(r, 1, !1, n, "http://www.w3.org/XML/1998/namespace", !1, !1);
  }), ["tabIndex", "crossOrigin"].forEach(function(n) {
    ct[n] = new at(n, 1, !1, n.toLowerCase(), null, !1, !1);
  }), ct.xlinkHref = new at("xlinkHref", 1, !1, "xlink:href", "http://www.w3.org/1999/xlink", !0, !1), ["src", "href", "action", "formAction"].forEach(function(n) {
    ct[n] = new at(n, 1, !1, n.toLowerCase(), null, !0, !0);
  });
  function Le(n, r, l, o) {
    var c = ct.hasOwnProperty(r) ? ct[r] : null;
    (c !== null ? c.type !== 0 : o || !(2 < r.length) || r[0] !== "o" && r[0] !== "O" || r[1] !== "n" && r[1] !== "N") && (Ve(r, l, c, o) && (l = null), o || c === null ? Se(r) && (l === null ? n.removeAttribute(r) : n.setAttribute(r, "" + l)) : c.mustUseProperty ? n[c.propertyName] = l === null ? c.type === 3 ? !1 : "" : l : (r = c.attributeName, o = c.attributeNamespace, l === null ? n.removeAttribute(r) : (c = c.type, l = c === 3 || c === 4 && l === !0 ? "" : "" + l, o ? n.setAttributeNS(o, r, l) : n.setAttribute(r, l))));
  }
  var it = I.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED, ke = Symbol.for("react.element"), Qe = Symbol.for("react.portal"), He = Symbol.for("react.fragment"), ln = Symbol.for("react.strict_mode"), Pt = Symbol.for("react.profiler"), Jt = Symbol.for("react.provider"), un = Symbol.for("react.context"), _t = Symbol.for("react.forward_ref"), Me = Symbol.for("react.suspense"), Ft = Symbol.for("react.suspense_list"), kt = Symbol.for("react.memo"), Ot = Symbol.for("react.lazy"), Re = Symbol.for("react.offscreen"), Z = Symbol.iterator;
  function we(n) {
    return n === null || typeof n != "object" ? null : (n = Z && n[Z] || n["@@iterator"], typeof n == "function" ? n : null);
  }
  var ne = Object.assign, _;
  function V(n) {
    if (_ === void 0) try {
      throw Error();
    } catch (l) {
      var r = l.stack.trim().match(/\n( *(at )?)/);
      _ = r && r[1] || "";
    }
    return `
` + _ + n;
  }
  var Ie = !1;
  function Pe(n, r) {
    if (!n || Ie) return "";
    Ie = !0;
    var l = Error.prepareStackTrace;
    Error.prepareStackTrace = void 0;
    try {
      if (r) if (r = function() {
        throw Error();
      }, Object.defineProperty(r.prototype, "props", { set: function() {
        throw Error();
      } }), typeof Reflect == "object" && Reflect.construct) {
        try {
          Reflect.construct(r, []);
        } catch (U) {
          var o = U;
        }
        Reflect.construct(n, [], r);
      } else {
        try {
          r.call();
        } catch (U) {
          o = U;
        }
        n.call(r.prototype);
      }
      else {
        try {
          throw Error();
        } catch (U) {
          o = U;
        }
        n();
      }
    } catch (U) {
      if (U && o && typeof U.stack == "string") {
        for (var c = U.stack.split(`
`), d = o.stack.split(`
`), m = c.length - 1, E = d.length - 1; 1 <= m && 0 <= E && c[m] !== d[E]; ) E--;
        for (; 1 <= m && 0 <= E; m--, E--) if (c[m] !== d[E]) {
          if (m !== 1 || E !== 1)
            do
              if (m--, E--, 0 > E || c[m] !== d[E]) {
                var T = `
` + c[m].replace(" at new ", " at ");
                return n.displayName && T.includes("<anonymous>") && (T = T.replace("<anonymous>", n.displayName)), T;
              }
            while (1 <= m && 0 <= E);
          break;
        }
      }
    } finally {
      Ie = !1, Error.prepareStackTrace = l;
    }
    return (n = n ? n.displayName || n.name : "") ? V(n) : "";
  }
  function ft(n) {
    switch (n.tag) {
      case 5:
        return V(n.type);
      case 16:
        return V("Lazy");
      case 13:
        return V("Suspense");
      case 19:
        return V("SuspenseList");
      case 0:
      case 2:
      case 15:
        return n = Pe(n.type, !1), n;
      case 11:
        return n = Pe(n.type.render, !1), n;
      case 1:
        return n = Pe(n.type, !0), n;
      default:
        return "";
    }
  }
  function lt(n) {
    if (n == null) return null;
    if (typeof n == "function") return n.displayName || n.name || null;
    if (typeof n == "string") return n;
    switch (n) {
      case He:
        return "Fragment";
      case Qe:
        return "Portal";
      case Pt:
        return "Profiler";
      case ln:
        return "StrictMode";
      case Me:
        return "Suspense";
      case Ft:
        return "SuspenseList";
    }
    if (typeof n == "object") switch (n.$$typeof) {
      case un:
        return (n.displayName || "Context") + ".Consumer";
      case Jt:
        return (n._context.displayName || "Context") + ".Provider";
      case _t:
        var r = n.render;
        return n = n.displayName, n || (n = r.displayName || r.name || "", n = n !== "" ? "ForwardRef(" + n + ")" : "ForwardRef"), n;
      case kt:
        return r = n.displayName || null, r !== null ? r : lt(n.type) || "Memo";
      case Ot:
        r = n._payload, n = n._init;
        try {
          return lt(n(r));
        } catch {
        }
    }
    return null;
  }
  function nt(n) {
    var r = n.type;
    switch (n.tag) {
      case 24:
        return "Cache";
      case 9:
        return (r.displayName || "Context") + ".Consumer";
      case 10:
        return (r._context.displayName || "Context") + ".Provider";
      case 18:
        return "DehydratedFragment";
      case 11:
        return n = r.render, n = n.displayName || n.name || "", r.displayName || (n !== "" ? "ForwardRef(" + n + ")" : "ForwardRef");
      case 7:
        return "Fragment";
      case 5:
        return r;
      case 4:
        return "Portal";
      case 3:
        return "Root";
      case 6:
        return "Text";
      case 16:
        return lt(r);
      case 8:
        return r === ln ? "StrictMode" : "Mode";
      case 22:
        return "Offscreen";
      case 12:
        return "Profiler";
      case 21:
        return "Scope";
      case 13:
        return "Suspense";
      case 19:
        return "SuspenseList";
      case 25:
        return "TracingMarker";
      case 1:
      case 0:
      case 17:
      case 2:
      case 14:
      case 15:
        if (typeof r == "function") return r.displayName || r.name || null;
        if (typeof r == "string") return r;
    }
    return null;
  }
  function ut(n) {
    switch (typeof n) {
      case "boolean":
      case "number":
      case "string":
      case "undefined":
        return n;
      case "object":
        return n;
      default:
        return "";
    }
  }
  function dt(n) {
    var r = n.type;
    return (n = n.nodeName) && n.toLowerCase() === "input" && (r === "checkbox" || r === "radio");
  }
  function It(n) {
    var r = dt(n) ? "checked" : "value", l = Object.getOwnPropertyDescriptor(n.constructor.prototype, r), o = "" + n[r];
    if (!n.hasOwnProperty(r) && typeof l < "u" && typeof l.get == "function" && typeof l.set == "function") {
      var c = l.get, d = l.set;
      return Object.defineProperty(n, r, { configurable: !0, get: function() {
        return c.call(this);
      }, set: function(m) {
        o = "" + m, d.call(this, m);
      } }), Object.defineProperty(n, r, { enumerable: l.enumerable }), { getValue: function() {
        return o;
      }, setValue: function(m) {
        o = "" + m;
      }, stopTracking: function() {
        n._valueTracker = null, delete n[r];
      } };
    }
  }
  function On(n) {
    n._valueTracker || (n._valueTracker = It(n));
  }
  function xr(n) {
    if (!n) return !1;
    var r = n._valueTracker;
    if (!r) return !0;
    var l = r.getValue(), o = "";
    return n && (o = dt(n) ? n.checked ? "true" : "false" : n.value), n = o, n !== l ? (r.setValue(n), !0) : !1;
  }
  function Cn(n) {
    if (n = n || (typeof document < "u" ? document : void 0), typeof n > "u") return null;
    try {
      return n.activeElement || n.body;
    } catch {
      return n.body;
    }
  }
  function nr(n, r) {
    var l = r.checked;
    return ne({}, r, { defaultChecked: void 0, defaultValue: void 0, value: void 0, checked: l ?? n._wrapperState.initialChecked });
  }
  function Vn(n, r) {
    var l = r.defaultValue == null ? "" : r.defaultValue, o = r.checked != null ? r.checked : r.defaultChecked;
    l = ut(r.value != null ? r.value : l), n._wrapperState = { initialChecked: o, initialValue: l, controlled: r.type === "checkbox" || r.type === "radio" ? r.checked != null : r.value != null };
  }
  function Bn(n, r) {
    r = r.checked, r != null && Le(n, "checked", r, !1);
  }
  function Yr(n, r) {
    Bn(n, r);
    var l = ut(r.value), o = r.type;
    if (l != null) o === "number" ? (l === 0 && n.value === "" || n.value != l) && (n.value = "" + l) : n.value !== "" + l && (n.value = "" + l);
    else if (o === "submit" || o === "reset") {
      n.removeAttribute("value");
      return;
    }
    r.hasOwnProperty("value") ? oa(n, r.type, l) : r.hasOwnProperty("defaultValue") && oa(n, r.type, ut(r.defaultValue)), r.checked == null && r.defaultChecked != null && (n.defaultChecked = !!r.defaultChecked);
  }
  function ci(n, r, l) {
    if (r.hasOwnProperty("value") || r.hasOwnProperty("defaultValue")) {
      var o = r.type;
      if (!(o !== "submit" && o !== "reset" || r.value !== void 0 && r.value !== null)) return;
      r = "" + n._wrapperState.initialValue, l || r === n.value || (n.value = r), n.defaultValue = r;
    }
    l = n.name, l !== "" && (n.name = ""), n.defaultChecked = !!n._wrapperState.initialChecked, l !== "" && (n.name = l);
  }
  function oa(n, r, l) {
    (r !== "number" || Cn(n.ownerDocument) !== n) && (l == null ? n.defaultValue = "" + n._wrapperState.initialValue : n.defaultValue !== "" + l && (n.defaultValue = "" + l));
  }
  var Kn = Array.isArray;
  function Rn(n, r, l, o) {
    if (n = n.options, r) {
      r = {};
      for (var c = 0; c < l.length; c++) r["$" + l[c]] = !0;
      for (l = 0; l < n.length; l++) c = r.hasOwnProperty("$" + n[l].value), n[l].selected !== c && (n[l].selected = c), c && o && (n[l].defaultSelected = !0);
    } else {
      for (l = "" + ut(l), r = null, c = 0; c < n.length; c++) {
        if (n[c].value === l) {
          n[c].selected = !0, o && (n[c].defaultSelected = !0);
          return;
        }
        r !== null || n[c].disabled || (r = n[c]);
      }
      r !== null && (r.selected = !0);
    }
  }
  function In(n, r) {
    if (r.dangerouslySetInnerHTML != null) throw Error(k(91));
    return ne({}, r, { value: void 0, defaultValue: void 0, children: "" + n._wrapperState.initialValue });
  }
  function gr(n, r) {
    var l = r.value;
    if (l == null) {
      if (l = r.children, r = r.defaultValue, l != null) {
        if (r != null) throw Error(k(92));
        if (Kn(l)) {
          if (1 < l.length) throw Error(k(93));
          l = l[0];
        }
        r = l;
      }
      r == null && (r = ""), l = r;
    }
    n._wrapperState = { initialValue: ut(l) };
  }
  function $a(n, r) {
    var l = ut(r.value), o = ut(r.defaultValue);
    l != null && (l = "" + l, l !== n.value && (n.value = l), r.defaultValue == null && n.defaultValue !== l && (n.defaultValue = l)), o != null && (n.defaultValue = "" + o);
  }
  function Ln(n) {
    var r = n.textContent;
    r === n._wrapperState.initialValue && r !== "" && r !== null && (n.value = r);
  }
  function Sr(n) {
    switch (n) {
      case "svg":
        return "http://www.w3.org/2000/svg";
      case "math":
        return "http://www.w3.org/1998/Math/MathML";
      default:
        return "http://www.w3.org/1999/xhtml";
    }
  }
  function sa(n, r) {
    return n == null || n === "http://www.w3.org/1999/xhtml" ? Sr(r) : n === "http://www.w3.org/2000/svg" && r === "foreignObject" ? "http://www.w3.org/1999/xhtml" : n;
  }
  var Qa, fi = function(n) {
    return typeof MSApp < "u" && MSApp.execUnsafeLocalFunction ? function(r, l, o, c) {
      MSApp.execUnsafeLocalFunction(function() {
        return n(r, l, o, c);
      });
    } : n;
  }(function(n, r) {
    if (n.namespaceURI !== "http://www.w3.org/2000/svg" || "innerHTML" in n) n.innerHTML = r;
    else {
      for (Qa = Qa || document.createElement("div"), Qa.innerHTML = "<svg>" + r.valueOf().toString() + "</svg>", r = Qa.firstChild; n.firstChild; ) n.removeChild(n.firstChild);
      for (; r.firstChild; ) n.appendChild(r.firstChild);
    }
  });
  function ee(n, r) {
    if (r) {
      var l = n.firstChild;
      if (l && l === n.lastChild && l.nodeType === 3) {
        l.nodeValue = r;
        return;
      }
    }
    n.textContent = r;
  }
  var xe = {
    animationIterationCount: !0,
    aspectRatio: !0,
    borderImageOutset: !0,
    borderImageSlice: !0,
    borderImageWidth: !0,
    boxFlex: !0,
    boxFlexGroup: !0,
    boxOrdinalGroup: !0,
    columnCount: !0,
    columns: !0,
    flex: !0,
    flexGrow: !0,
    flexPositive: !0,
    flexShrink: !0,
    flexNegative: !0,
    flexOrder: !0,
    gridArea: !0,
    gridRow: !0,
    gridRowEnd: !0,
    gridRowSpan: !0,
    gridRowStart: !0,
    gridColumn: !0,
    gridColumnEnd: !0,
    gridColumnSpan: !0,
    gridColumnStart: !0,
    fontWeight: !0,
    lineClamp: !0,
    lineHeight: !0,
    opacity: !0,
    order: !0,
    orphans: !0,
    tabSize: !0,
    widows: !0,
    zIndex: !0,
    zoom: !0,
    fillOpacity: !0,
    floodOpacity: !0,
    stopOpacity: !0,
    strokeDasharray: !0,
    strokeDashoffset: !0,
    strokeMiterlimit: !0,
    strokeOpacity: !0,
    strokeWidth: !0
  }, ot = ["Webkit", "ms", "Moz", "O"];
  Object.keys(xe).forEach(function(n) {
    ot.forEach(function(r) {
      r = r + n.charAt(0).toUpperCase() + n.substring(1), xe[r] = xe[n];
    });
  });
  function Ht(n, r, l) {
    return r == null || typeof r == "boolean" || r === "" ? "" : l || typeof r != "number" || r === 0 || xe.hasOwnProperty(n) && xe[n] ? ("" + r).trim() : r + "px";
  }
  function en(n, r) {
    n = n.style;
    for (var l in r) if (r.hasOwnProperty(l)) {
      var o = l.indexOf("--") === 0, c = Ht(l, r[l], o);
      l === "float" && (l = "cssFloat"), o ? n.setProperty(l, c) : n[l] = c;
    }
  }
  var vn = ne({ menuitem: !0 }, { area: !0, base: !0, br: !0, col: !0, embed: !0, hr: !0, img: !0, input: !0, keygen: !0, link: !0, meta: !0, param: !0, source: !0, track: !0, wbr: !0 });
  function on(n, r) {
    if (r) {
      if (vn[n] && (r.children != null || r.dangerouslySetInnerHTML != null)) throw Error(k(137, n));
      if (r.dangerouslySetInnerHTML != null) {
        if (r.children != null) throw Error(k(60));
        if (typeof r.dangerouslySetInnerHTML != "object" || !("__html" in r.dangerouslySetInnerHTML)) throw Error(k(61));
      }
      if (r.style != null && typeof r.style != "object") throw Error(k(62));
    }
  }
  function qn(n, r) {
    if (n.indexOf("-") === -1) return typeof r.is == "string";
    switch (n) {
      case "annotation-xml":
      case "color-profile":
      case "font-face":
      case "font-face-src":
      case "font-face-uri":
      case "font-face-format":
      case "font-face-name":
      case "missing-glyph":
        return !1;
      default:
        return !0;
    }
  }
  var tn = null;
  function Yt(n) {
    return n = n.target || n.srcElement || window, n.correspondingUseElement && (n = n.correspondingUseElement), n.nodeType === 3 ? n.parentNode : n;
  }
  var $t = null, ca = null, Er = null;
  function Ta(n) {
    if (n = De(n)) {
      if (typeof $t != "function") throw Error(k(280));
      var r = n.stateNode;
      r && (r = mn(r), $t(n.stateNode, n.type, r));
    }
  }
  function Hi(n) {
    ca ? Er ? Er.push(n) : Er = [n] : ca = n;
  }
  function Jl() {
    if (ca) {
      var n = ca, r = Er;
      if (Er = ca = null, Ta(n), r) for (n = 0; n < r.length; n++) Ta(r[n]);
    }
  }
  function eu(n, r) {
    return n(r);
  }
  function pl() {
  }
  var vl = !1;
  function tu(n, r, l) {
    if (vl) return n(r, l);
    vl = !0;
    try {
      return eu(n, r, l);
    } finally {
      vl = !1, (ca !== null || Er !== null) && (pl(), Jl());
    }
  }
  function br(n, r) {
    var l = n.stateNode;
    if (l === null) return null;
    var o = mn(l);
    if (o === null) return null;
    l = o[r];
    e: switch (r) {
      case "onClick":
      case "onClickCapture":
      case "onDoubleClick":
      case "onDoubleClickCapture":
      case "onMouseDown":
      case "onMouseDownCapture":
      case "onMouseMove":
      case "onMouseMoveCapture":
      case "onMouseUp":
      case "onMouseUpCapture":
      case "onMouseEnter":
        (o = !o.disabled) || (n = n.type, o = !(n === "button" || n === "input" || n === "select" || n === "textarea")), n = !o;
        break e;
      default:
        n = !1;
    }
    if (n) return null;
    if (l && typeof l != "function") throw Error(k(231, r, typeof l));
    return l;
  }
  var _r = !1;
  if (Et) try {
    var rr = {};
    Object.defineProperty(rr, "passive", { get: function() {
      _r = !0;
    } }), window.addEventListener("test", rr, rr), window.removeEventListener("test", rr, rr);
  } catch {
    _r = !1;
  }
  function di(n, r, l, o, c, d, m, E, T) {
    var U = Array.prototype.slice.call(arguments, 3);
    try {
      r.apply(l, U);
    } catch (W) {
      this.onError(W);
    }
  }
  var Wa = !1, pi = null, vi = !1, R = null, Y = { onError: function(n) {
    Wa = !0, pi = n;
  } };
  function ie(n, r, l, o, c, d, m, E, T) {
    Wa = !1, pi = null, di.apply(Y, arguments);
  }
  function he(n, r, l, o, c, d, m, E, T) {
    if (ie.apply(this, arguments), Wa) {
      if (Wa) {
        var U = pi;
        Wa = !1, pi = null;
      } else throw Error(k(198));
      vi || (vi = !0, R = U);
    }
  }
  function Ze(n) {
    var r = n, l = n;
    if (n.alternate) for (; r.return; ) r = r.return;
    else {
      n = r;
      do
        r = n, r.flags & 4098 && (l = r.return), n = r.return;
      while (n);
    }
    return r.tag === 3 ? l : null;
  }
  function Ge(n) {
    if (n.tag === 13) {
      var r = n.memoizedState;
      if (r === null && (n = n.alternate, n !== null && (r = n.memoizedState)), r !== null) return r.dehydrated;
    }
    return null;
  }
  function ht(n) {
    if (Ze(n) !== n) throw Error(k(188));
  }
  function pt(n) {
    var r = n.alternate;
    if (!r) {
      if (r = Ze(n), r === null) throw Error(k(188));
      return r !== n ? null : n;
    }
    for (var l = n, o = r; ; ) {
      var c = l.return;
      if (c === null) break;
      var d = c.alternate;
      if (d === null) {
        if (o = c.return, o !== null) {
          l = o;
          continue;
        }
        break;
      }
      if (c.child === d.child) {
        for (d = c.child; d; ) {
          if (d === l) return ht(c), n;
          if (d === o) return ht(c), r;
          d = d.sibling;
        }
        throw Error(k(188));
      }
      if (l.return !== o.return) l = c, o = d;
      else {
        for (var m = !1, E = c.child; E; ) {
          if (E === l) {
            m = !0, l = c, o = d;
            break;
          }
          if (E === o) {
            m = !0, o = c, l = d;
            break;
          }
          E = E.sibling;
        }
        if (!m) {
          for (E = d.child; E; ) {
            if (E === l) {
              m = !0, l = d, o = c;
              break;
            }
            if (E === o) {
              m = !0, o = d, l = c;
              break;
            }
            E = E.sibling;
          }
          if (!m) throw Error(k(189));
        }
      }
      if (l.alternate !== o) throw Error(k(190));
    }
    if (l.tag !== 3) throw Error(k(188));
    return l.stateNode.current === l ? n : r;
  }
  function Tn(n) {
    return n = pt(n), n !== null ? nn(n) : null;
  }
  function nn(n) {
    if (n.tag === 5 || n.tag === 6) return n;
    for (n = n.child; n !== null; ) {
      var r = nn(n);
      if (r !== null) return r;
      n = n.sibling;
    }
    return null;
  }
  var sn = j.unstable_scheduleCallback, ar = j.unstable_cancelCallback, Ga = j.unstable_shouldYield, Ka = j.unstable_requestPaint, Je = j.unstable_now, rt = j.unstable_getCurrentPriorityLevel, qa = j.unstable_ImmediatePriority, nu = j.unstable_UserBlockingPriority, ru = j.unstable_NormalPriority, hl = j.unstable_LowPriority, Wu = j.unstable_IdlePriority, ml = null, $r = null;
  function $o(n) {
    if ($r && typeof $r.onCommitFiberRoot == "function") try {
      $r.onCommitFiberRoot(ml, n, void 0, (n.current.flags & 128) === 128);
    } catch {
    }
  }
  var kr = Math.clz32 ? Math.clz32 : Gu, lc = Math.log, uc = Math.LN2;
  function Gu(n) {
    return n >>>= 0, n === 0 ? 32 : 31 - (lc(n) / uc | 0) | 0;
  }
  var yl = 64, fa = 4194304;
  function Xa(n) {
    switch (n & -n) {
      case 1:
        return 1;
      case 2:
        return 2;
      case 4:
        return 4;
      case 8:
        return 8;
      case 16:
        return 16;
      case 32:
        return 32;
      case 64:
      case 128:
      case 256:
      case 512:
      case 1024:
      case 2048:
      case 4096:
      case 8192:
      case 16384:
      case 32768:
      case 65536:
      case 131072:
      case 262144:
      case 524288:
      case 1048576:
      case 2097152:
        return n & 4194240;
      case 4194304:
      case 8388608:
      case 16777216:
      case 33554432:
      case 67108864:
        return n & 130023424;
      case 134217728:
        return 134217728;
      case 268435456:
        return 268435456;
      case 536870912:
        return 536870912;
      case 1073741824:
        return 1073741824;
      default:
        return n;
    }
  }
  function Za(n, r) {
    var l = n.pendingLanes;
    if (l === 0) return 0;
    var o = 0, c = n.suspendedLanes, d = n.pingedLanes, m = l & 268435455;
    if (m !== 0) {
      var E = m & ~c;
      E !== 0 ? o = Xa(E) : (d &= m, d !== 0 && (o = Xa(d)));
    } else m = l & ~c, m !== 0 ? o = Xa(m) : d !== 0 && (o = Xa(d));
    if (o === 0) return 0;
    if (r !== 0 && r !== o && !(r & c) && (c = o & -o, d = r & -r, c >= d || c === 16 && (d & 4194240) !== 0)) return r;
    if (o & 4 && (o |= l & 16), r = n.entangledLanes, r !== 0) for (n = n.entanglements, r &= o; 0 < r; ) l = 31 - kr(r), c = 1 << l, o |= n[l], r &= ~c;
    return o;
  }
  function Ku(n, r) {
    switch (n) {
      case 1:
      case 2:
      case 4:
        return r + 250;
      case 8:
      case 16:
      case 32:
      case 64:
      case 128:
      case 256:
      case 512:
      case 1024:
      case 2048:
      case 4096:
      case 8192:
      case 16384:
      case 32768:
      case 65536:
      case 131072:
      case 262144:
      case 524288:
      case 1048576:
      case 2097152:
        return r + 5e3;
      case 4194304:
      case 8388608:
      case 16777216:
      case 33554432:
      case 67108864:
        return -1;
      case 134217728:
      case 268435456:
      case 536870912:
      case 1073741824:
        return -1;
      default:
        return -1;
    }
  }
  function au(n, r) {
    for (var l = n.suspendedLanes, o = n.pingedLanes, c = n.expirationTimes, d = n.pendingLanes; 0 < d; ) {
      var m = 31 - kr(d), E = 1 << m, T = c[m];
      T === -1 ? (!(E & l) || E & o) && (c[m] = Ku(E, r)) : T <= r && (n.expiredLanes |= E), d &= ~E;
    }
  }
  function gl(n) {
    return n = n.pendingLanes & -1073741825, n !== 0 ? n : n & 1073741824 ? 1073741824 : 0;
  }
  function qu() {
    var n = yl;
    return yl <<= 1, !(yl & 4194240) && (yl = 64), n;
  }
  function Xu(n) {
    for (var r = [], l = 0; 31 > l; l++) r.push(n);
    return r;
  }
  function Pi(n, r, l) {
    n.pendingLanes |= r, r !== 536870912 && (n.suspendedLanes = 0, n.pingedLanes = 0), n = n.eventTimes, r = 31 - kr(r), n[r] = l;
  }
  function Qf(n, r) {
    var l = n.pendingLanes & ~r;
    n.pendingLanes = r, n.suspendedLanes = 0, n.pingedLanes = 0, n.expiredLanes &= r, n.mutableReadLanes &= r, n.entangledLanes &= r, r = n.entanglements;
    var o = n.eventTimes;
    for (n = n.expirationTimes; 0 < l; ) {
      var c = 31 - kr(l), d = 1 << c;
      r[c] = 0, o[c] = -1, n[c] = -1, l &= ~d;
    }
  }
  function Vi(n, r) {
    var l = n.entangledLanes |= r;
    for (n = n.entanglements; l; ) {
      var o = 31 - kr(l), c = 1 << o;
      c & r | n[o] & r && (n[o] |= r), l &= ~c;
    }
  }
  var Lt = 0;
  function Zu(n) {
    return n &= -n, 1 < n ? 4 < n ? n & 268435455 ? 16 : 536870912 : 4 : 1;
  }
  var xt, Qo, hi, We, Ju, ir = !1, mi = [], Dr = null, yi = null, cn = null, Qt = /* @__PURE__ */ new Map(), Sl = /* @__PURE__ */ new Map(), Yn = [], Or = "mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");
  function wa(n, r) {
    switch (n) {
      case "focusin":
      case "focusout":
        Dr = null;
        break;
      case "dragenter":
      case "dragleave":
        yi = null;
        break;
      case "mouseover":
      case "mouseout":
        cn = null;
        break;
      case "pointerover":
      case "pointerout":
        Qt.delete(r.pointerId);
        break;
      case "gotpointercapture":
      case "lostpointercapture":
        Sl.delete(r.pointerId);
    }
  }
  function iu(n, r, l, o, c, d) {
    return n === null || n.nativeEvent !== d ? (n = { blockedOn: r, domEventName: l, eventSystemFlags: o, nativeEvent: d, targetContainers: [c] }, r !== null && (r = De(r), r !== null && Qo(r)), n) : (n.eventSystemFlags |= o, r = n.targetContainers, c !== null && r.indexOf(c) === -1 && r.push(c), n);
  }
  function Wo(n, r, l, o, c) {
    switch (r) {
      case "focusin":
        return Dr = iu(Dr, n, r, l, o, c), !0;
      case "dragenter":
        return yi = iu(yi, n, r, l, o, c), !0;
      case "mouseover":
        return cn = iu(cn, n, r, l, o, c), !0;
      case "pointerover":
        var d = c.pointerId;
        return Qt.set(d, iu(Qt.get(d) || null, n, r, l, o, c)), !0;
      case "gotpointercapture":
        return d = c.pointerId, Sl.set(d, iu(Sl.get(d) || null, n, r, l, o, c)), !0;
    }
    return !1;
  }
  function Go(n) {
    var r = vu(n.target);
    if (r !== null) {
      var l = Ze(r);
      if (l !== null) {
        if (r = l.tag, r === 13) {
          if (r = Ge(l), r !== null) {
            n.blockedOn = r, Ju(n.priority, function() {
              hi(l);
            });
            return;
          }
        } else if (r === 3 && l.stateNode.current.memoizedState.isDehydrated) {
          n.blockedOn = l.tag === 3 ? l.stateNode.containerInfo : null;
          return;
        }
      }
    }
    n.blockedOn = null;
  }
  function El(n) {
    if (n.blockedOn !== null) return !1;
    for (var r = n.targetContainers; 0 < r.length; ) {
      var l = no(n.domEventName, n.eventSystemFlags, r[0], n.nativeEvent);
      if (l === null) {
        l = n.nativeEvent;
        var o = new l.constructor(l.type, l);
        tn = o, l.target.dispatchEvent(o), tn = null;
      } else return r = De(l), r !== null && Qo(r), n.blockedOn = l, !1;
      r.shift();
    }
    return !0;
  }
  function lu(n, r, l) {
    El(n) && l.delete(r);
  }
  function Wf() {
    ir = !1, Dr !== null && El(Dr) && (Dr = null), yi !== null && El(yi) && (yi = null), cn !== null && El(cn) && (cn = null), Qt.forEach(lu), Sl.forEach(lu);
  }
  function xa(n, r) {
    n.blockedOn === r && (n.blockedOn = null, ir || (ir = !0, j.unstable_scheduleCallback(j.unstable_NormalPriority, Wf)));
  }
  function Ja(n) {
    function r(c) {
      return xa(c, n);
    }
    if (0 < mi.length) {
      xa(mi[0], n);
      for (var l = 1; l < mi.length; l++) {
        var o = mi[l];
        o.blockedOn === n && (o.blockedOn = null);
      }
    }
    for (Dr !== null && xa(Dr, n), yi !== null && xa(yi, n), cn !== null && xa(cn, n), Qt.forEach(r), Sl.forEach(r), l = 0; l < Yn.length; l++) o = Yn[l], o.blockedOn === n && (o.blockedOn = null);
    for (; 0 < Yn.length && (l = Yn[0], l.blockedOn === null); ) Go(l), l.blockedOn === null && Yn.shift();
  }
  var gi = it.ReactCurrentBatchConfig, ba = !0;
  function eo(n, r, l, o) {
    var c = Lt, d = gi.transition;
    gi.transition = null;
    try {
      Lt = 1, Cl(n, r, l, o);
    } finally {
      Lt = c, gi.transition = d;
    }
  }
  function to(n, r, l, o) {
    var c = Lt, d = gi.transition;
    gi.transition = null;
    try {
      Lt = 4, Cl(n, r, l, o);
    } finally {
      Lt = c, gi.transition = d;
    }
  }
  function Cl(n, r, l, o) {
    if (ba) {
      var c = no(n, r, l, o);
      if (c === null) Sc(n, r, o, uu, l), wa(n, o);
      else if (Wo(c, n, r, l, o)) o.stopPropagation();
      else if (wa(n, o), r & 4 && -1 < Or.indexOf(n)) {
        for (; c !== null; ) {
          var d = De(c);
          if (d !== null && xt(d), d = no(n, r, l, o), d === null && Sc(n, r, o, uu, l), d === c) break;
          c = d;
        }
        c !== null && o.stopPropagation();
      } else Sc(n, r, o, null, l);
    }
  }
  var uu = null;
  function no(n, r, l, o) {
    if (uu = null, n = Yt(o), n = vu(n), n !== null) if (r = Ze(n), r === null) n = null;
    else if (l = r.tag, l === 13) {
      if (n = Ge(r), n !== null) return n;
      n = null;
    } else if (l === 3) {
      if (r.stateNode.current.memoizedState.isDehydrated) return r.tag === 3 ? r.stateNode.containerInfo : null;
      n = null;
    } else r !== n && (n = null);
    return uu = n, null;
  }
  function ro(n) {
    switch (n) {
      case "cancel":
      case "click":
      case "close":
      case "contextmenu":
      case "copy":
      case "cut":
      case "auxclick":
      case "dblclick":
      case "dragend":
      case "dragstart":
      case "drop":
      case "focusin":
      case "focusout":
      case "input":
      case "invalid":
      case "keydown":
      case "keypress":
      case "keyup":
      case "mousedown":
      case "mouseup":
      case "paste":
      case "pause":
      case "play":
      case "pointercancel":
      case "pointerdown":
      case "pointerup":
      case "ratechange":
      case "reset":
      case "resize":
      case "seeked":
      case "submit":
      case "touchcancel":
      case "touchend":
      case "touchstart":
      case "volumechange":
      case "change":
      case "selectionchange":
      case "textInput":
      case "compositionstart":
      case "compositionend":
      case "compositionupdate":
      case "beforeblur":
      case "afterblur":
      case "beforeinput":
      case "blur":
      case "fullscreenchange":
      case "focus":
      case "hashchange":
      case "popstate":
      case "select":
      case "selectstart":
        return 1;
      case "drag":
      case "dragenter":
      case "dragexit":
      case "dragleave":
      case "dragover":
      case "mousemove":
      case "mouseout":
      case "mouseover":
      case "pointermove":
      case "pointerout":
      case "pointerover":
      case "scroll":
      case "toggle":
      case "touchmove":
      case "wheel":
      case "mouseenter":
      case "mouseleave":
      case "pointerenter":
      case "pointerleave":
        return 4;
      case "message":
        switch (rt()) {
          case qa:
            return 1;
          case nu:
            return 4;
          case ru:
          case hl:
            return 16;
          case Wu:
            return 536870912;
          default:
            return 16;
        }
      default:
        return 16;
    }
  }
  var ei = null, h = null, C = null;
  function z() {
    if (C) return C;
    var n, r = h, l = r.length, o, c = "value" in ei ? ei.value : ei.textContent, d = c.length;
    for (n = 0; n < l && r[n] === c[n]; n++) ;
    var m = l - n;
    for (o = 1; o <= m && r[l - o] === c[d - o]; o++) ;
    return C = c.slice(n, 1 < o ? 1 - o : void 0);
  }
  function F(n) {
    var r = n.keyCode;
    return "charCode" in n ? (n = n.charCode, n === 0 && r === 13 && (n = 13)) : n = r, n === 10 && (n = 13), 32 <= n || n === 13 ? n : 0;
  }
  function X() {
    return !0;
  }
  function Ne() {
    return !1;
  }
  function re(n) {
    function r(l, o, c, d, m) {
      this._reactName = l, this._targetInst = c, this.type = o, this.nativeEvent = d, this.target = m, this.currentTarget = null;
      for (var E in n) n.hasOwnProperty(E) && (l = n[E], this[E] = l ? l(d) : d[E]);
      return this.isDefaultPrevented = (d.defaultPrevented != null ? d.defaultPrevented : d.returnValue === !1) ? X : Ne, this.isPropagationStopped = Ne, this;
    }
    return ne(r.prototype, { preventDefault: function() {
      this.defaultPrevented = !0;
      var l = this.nativeEvent;
      l && (l.preventDefault ? l.preventDefault() : typeof l.returnValue != "unknown" && (l.returnValue = !1), this.isDefaultPrevented = X);
    }, stopPropagation: function() {
      var l = this.nativeEvent;
      l && (l.stopPropagation ? l.stopPropagation() : typeof l.cancelBubble != "unknown" && (l.cancelBubble = !0), this.isPropagationStopped = X);
    }, persist: function() {
    }, isPersistent: X }), r;
  }
  var Ae = { eventPhase: 0, bubbles: 0, cancelable: 0, timeStamp: function(n) {
    return n.timeStamp || Date.now();
  }, defaultPrevented: 0, isTrusted: 0 }, mt = re(Ae), bt = ne({}, Ae, { view: 0, detail: 0 }), rn = re(bt), Wt, st, Gt, hn = ne({}, bt, { screenX: 0, screenY: 0, clientX: 0, clientY: 0, pageX: 0, pageY: 0, ctrlKey: 0, shiftKey: 0, altKey: 0, metaKey: 0, getModifierState: Zf, button: 0, buttons: 0, relatedTarget: function(n) {
    return n.relatedTarget === void 0 ? n.fromElement === n.srcElement ? n.toElement : n.fromElement : n.relatedTarget;
  }, movementX: function(n) {
    return "movementX" in n ? n.movementX : (n !== Gt && (Gt && n.type === "mousemove" ? (Wt = n.screenX - Gt.screenX, st = n.screenY - Gt.screenY) : st = Wt = 0, Gt = n), Wt);
  }, movementY: function(n) {
    return "movementY" in n ? n.movementY : st;
  } }), Rl = re(hn), Ko = ne({}, hn, { dataTransfer: 0 }), Bi = re(Ko), qo = ne({}, bt, { relatedTarget: 0 }), ou = re(qo), Gf = ne({}, Ae, { animationName: 0, elapsedTime: 0, pseudoElement: 0 }), oc = re(Gf), Kf = ne({}, Ae, { clipboardData: function(n) {
    return "clipboardData" in n ? n.clipboardData : window.clipboardData;
  } }), ev = re(Kf), qf = ne({}, Ae, { data: 0 }), Xf = re(qf), tv = {
    Esc: "Escape",
    Spacebar: " ",
    Left: "ArrowLeft",
    Up: "ArrowUp",
    Right: "ArrowRight",
    Down: "ArrowDown",
    Del: "Delete",
    Win: "OS",
    Menu: "ContextMenu",
    Apps: "ContextMenu",
    Scroll: "ScrollLock",
    MozPrintableKey: "Unidentified"
  }, nv = {
    8: "Backspace",
    9: "Tab",
    12: "Clear",
    13: "Enter",
    16: "Shift",
    17: "Control",
    18: "Alt",
    19: "Pause",
    20: "CapsLock",
    27: "Escape",
    32: " ",
    33: "PageUp",
    34: "PageDown",
    35: "End",
    36: "Home",
    37: "ArrowLeft",
    38: "ArrowUp",
    39: "ArrowRight",
    40: "ArrowDown",
    45: "Insert",
    46: "Delete",
    112: "F1",
    113: "F2",
    114: "F3",
    115: "F4",
    116: "F5",
    117: "F6",
    118: "F7",
    119: "F8",
    120: "F9",
    121: "F10",
    122: "F11",
    123: "F12",
    144: "NumLock",
    145: "ScrollLock",
    224: "Meta"
  }, Wm = { Alt: "altKey", Control: "ctrlKey", Meta: "metaKey", Shift: "shiftKey" };
  function Ii(n) {
    var r = this.nativeEvent;
    return r.getModifierState ? r.getModifierState(n) : (n = Wm[n]) ? !!r[n] : !1;
  }
  function Zf() {
    return Ii;
  }
  var Jf = ne({}, bt, { key: function(n) {
    if (n.key) {
      var r = tv[n.key] || n.key;
      if (r !== "Unidentified") return r;
    }
    return n.type === "keypress" ? (n = F(n), n === 13 ? "Enter" : String.fromCharCode(n)) : n.type === "keydown" || n.type === "keyup" ? nv[n.keyCode] || "Unidentified" : "";
  }, code: 0, location: 0, ctrlKey: 0, shiftKey: 0, altKey: 0, metaKey: 0, repeat: 0, locale: 0, getModifierState: Zf, charCode: function(n) {
    return n.type === "keypress" ? F(n) : 0;
  }, keyCode: function(n) {
    return n.type === "keydown" || n.type === "keyup" ? n.keyCode : 0;
  }, which: function(n) {
    return n.type === "keypress" ? F(n) : n.type === "keydown" || n.type === "keyup" ? n.keyCode : 0;
  } }), ed = re(Jf), td = ne({}, hn, { pointerId: 0, width: 0, height: 0, pressure: 0, tangentialPressure: 0, tiltX: 0, tiltY: 0, twist: 0, pointerType: 0, isPrimary: 0 }), rv = re(td), sc = ne({}, bt, { touches: 0, targetTouches: 0, changedTouches: 0, altKey: 0, metaKey: 0, ctrlKey: 0, shiftKey: 0, getModifierState: Zf }), av = re(sc), Qr = ne({}, Ae, { propertyName: 0, elapsedTime: 0, pseudoElement: 0 }), Yi = re(Qr), Mn = ne({}, hn, {
    deltaX: function(n) {
      return "deltaX" in n ? n.deltaX : "wheelDeltaX" in n ? -n.wheelDeltaX : 0;
    },
    deltaY: function(n) {
      return "deltaY" in n ? n.deltaY : "wheelDeltaY" in n ? -n.wheelDeltaY : "wheelDelta" in n ? -n.wheelDelta : 0;
    },
    deltaZ: 0,
    deltaMode: 0
  }), $i = re(Mn), nd = [9, 13, 27, 32], ao = Et && "CompositionEvent" in window, Xo = null;
  Et && "documentMode" in document && (Xo = document.documentMode);
  var Zo = Et && "TextEvent" in window && !Xo, iv = Et && (!ao || Xo && 8 < Xo && 11 >= Xo), lv = " ", cc = !1;
  function uv(n, r) {
    switch (n) {
      case "keyup":
        return nd.indexOf(r.keyCode) !== -1;
      case "keydown":
        return r.keyCode !== 229;
      case "keypress":
      case "mousedown":
      case "focusout":
        return !0;
      default:
        return !1;
    }
  }
  function ov(n) {
    return n = n.detail, typeof n == "object" && "data" in n ? n.data : null;
  }
  var io = !1;
  function sv(n, r) {
    switch (n) {
      case "compositionend":
        return ov(r);
      case "keypress":
        return r.which !== 32 ? null : (cc = !0, lv);
      case "textInput":
        return n = r.data, n === lv && cc ? null : n;
      default:
        return null;
    }
  }
  function Gm(n, r) {
    if (io) return n === "compositionend" || !ao && uv(n, r) ? (n = z(), C = h = ei = null, io = !1, n) : null;
    switch (n) {
      case "paste":
        return null;
      case "keypress":
        if (!(r.ctrlKey || r.altKey || r.metaKey) || r.ctrlKey && r.altKey) {
          if (r.char && 1 < r.char.length) return r.char;
          if (r.which) return String.fromCharCode(r.which);
        }
        return null;
      case "compositionend":
        return iv && r.locale !== "ko" ? null : r.data;
      default:
        return null;
    }
  }
  var Km = { color: !0, date: !0, datetime: !0, "datetime-local": !0, email: !0, month: !0, number: !0, password: !0, range: !0, search: !0, tel: !0, text: !0, time: !0, url: !0, week: !0 };
  function cv(n) {
    var r = n && n.nodeName && n.nodeName.toLowerCase();
    return r === "input" ? !!Km[n.type] : r === "textarea";
  }
  function rd(n, r, l, o) {
    Hi(o), r = as(r, "onChange"), 0 < r.length && (l = new mt("onChange", "change", null, l, o), n.push({ event: l, listeners: r }));
  }
  var Si = null, su = null;
  function fv(n) {
    du(n, 0);
  }
  function Jo(n) {
    var r = ni(n);
    if (xr(r)) return n;
  }
  function qm(n, r) {
    if (n === "change") return r;
  }
  var dv = !1;
  if (Et) {
    var ad;
    if (Et) {
      var id = "oninput" in document;
      if (!id) {
        var pv = document.createElement("div");
        pv.setAttribute("oninput", "return;"), id = typeof pv.oninput == "function";
      }
      ad = id;
    } else ad = !1;
    dv = ad && (!document.documentMode || 9 < document.documentMode);
  }
  function vv() {
    Si && (Si.detachEvent("onpropertychange", hv), su = Si = null);
  }
  function hv(n) {
    if (n.propertyName === "value" && Jo(su)) {
      var r = [];
      rd(r, su, n, Yt(n)), tu(fv, r);
    }
  }
  function Xm(n, r, l) {
    n === "focusin" ? (vv(), Si = r, su = l, Si.attachEvent("onpropertychange", hv)) : n === "focusout" && vv();
  }
  function mv(n) {
    if (n === "selectionchange" || n === "keyup" || n === "keydown") return Jo(su);
  }
  function Zm(n, r) {
    if (n === "click") return Jo(r);
  }
  function yv(n, r) {
    if (n === "input" || n === "change") return Jo(r);
  }
  function Jm(n, r) {
    return n === r && (n !== 0 || 1 / n === 1 / r) || n !== n && r !== r;
  }
  var ti = typeof Object.is == "function" ? Object.is : Jm;
  function es(n, r) {
    if (ti(n, r)) return !0;
    if (typeof n != "object" || n === null || typeof r != "object" || r === null) return !1;
    var l = Object.keys(n), o = Object.keys(r);
    if (l.length !== o.length) return !1;
    for (o = 0; o < l.length; o++) {
      var c = l[o];
      if (!se.call(r, c) || !ti(n[c], r[c])) return !1;
    }
    return !0;
  }
  function gv(n) {
    for (; n && n.firstChild; ) n = n.firstChild;
    return n;
  }
  function fc(n, r) {
    var l = gv(n);
    n = 0;
    for (var o; l; ) {
      if (l.nodeType === 3) {
        if (o = n + l.textContent.length, n <= r && o >= r) return { node: l, offset: r - n };
        n = o;
      }
      e: {
        for (; l; ) {
          if (l.nextSibling) {
            l = l.nextSibling;
            break e;
          }
          l = l.parentNode;
        }
        l = void 0;
      }
      l = gv(l);
    }
  }
  function Tl(n, r) {
    return n && r ? n === r ? !0 : n && n.nodeType === 3 ? !1 : r && r.nodeType === 3 ? Tl(n, r.parentNode) : "contains" in n ? n.contains(r) : n.compareDocumentPosition ? !!(n.compareDocumentPosition(r) & 16) : !1 : !1;
  }
  function ts() {
    for (var n = window, r = Cn(); r instanceof n.HTMLIFrameElement; ) {
      try {
        var l = typeof r.contentWindow.location.href == "string";
      } catch {
        l = !1;
      }
      if (l) n = r.contentWindow;
      else break;
      r = Cn(n.document);
    }
    return r;
  }
  function dc(n) {
    var r = n && n.nodeName && n.nodeName.toLowerCase();
    return r && (r === "input" && (n.type === "text" || n.type === "search" || n.type === "tel" || n.type === "url" || n.type === "password") || r === "textarea" || n.contentEditable === "true");
  }
  function lo(n) {
    var r = ts(), l = n.focusedElem, o = n.selectionRange;
    if (r !== l && l && l.ownerDocument && Tl(l.ownerDocument.documentElement, l)) {
      if (o !== null && dc(l)) {
        if (r = o.start, n = o.end, n === void 0 && (n = r), "selectionStart" in l) l.selectionStart = r, l.selectionEnd = Math.min(n, l.value.length);
        else if (n = (r = l.ownerDocument || document) && r.defaultView || window, n.getSelection) {
          n = n.getSelection();
          var c = l.textContent.length, d = Math.min(o.start, c);
          o = o.end === void 0 ? d : Math.min(o.end, c), !n.extend && d > o && (c = o, o = d, d = c), c = fc(l, d);
          var m = fc(
            l,
            o
          );
          c && m && (n.rangeCount !== 1 || n.anchorNode !== c.node || n.anchorOffset !== c.offset || n.focusNode !== m.node || n.focusOffset !== m.offset) && (r = r.createRange(), r.setStart(c.node, c.offset), n.removeAllRanges(), d > o ? (n.addRange(r), n.extend(m.node, m.offset)) : (r.setEnd(m.node, m.offset), n.addRange(r)));
        }
      }
      for (r = [], n = l; n = n.parentNode; ) n.nodeType === 1 && r.push({ element: n, left: n.scrollLeft, top: n.scrollTop });
      for (typeof l.focus == "function" && l.focus(), l = 0; l < r.length; l++) n = r[l], n.element.scrollLeft = n.left, n.element.scrollTop = n.top;
    }
  }
  var ey = Et && "documentMode" in document && 11 >= document.documentMode, uo = null, ld = null, ns = null, ud = !1;
  function od(n, r, l) {
    var o = l.window === l ? l.document : l.nodeType === 9 ? l : l.ownerDocument;
    ud || uo == null || uo !== Cn(o) || (o = uo, "selectionStart" in o && dc(o) ? o = { start: o.selectionStart, end: o.selectionEnd } : (o = (o.ownerDocument && o.ownerDocument.defaultView || window).getSelection(), o = { anchorNode: o.anchorNode, anchorOffset: o.anchorOffset, focusNode: o.focusNode, focusOffset: o.focusOffset }), ns && es(ns, o) || (ns = o, o = as(ld, "onSelect"), 0 < o.length && (r = new mt("onSelect", "select", null, r, l), n.push({ event: r, listeners: o }), r.target = uo)));
  }
  function pc(n, r) {
    var l = {};
    return l[n.toLowerCase()] = r.toLowerCase(), l["Webkit" + n] = "webkit" + r, l["Moz" + n] = "moz" + r, l;
  }
  var cu = { animationend: pc("Animation", "AnimationEnd"), animationiteration: pc("Animation", "AnimationIteration"), animationstart: pc("Animation", "AnimationStart"), transitionend: pc("Transition", "TransitionEnd") }, lr = {}, sd = {};
  Et && (sd = document.createElement("div").style, "AnimationEvent" in window || (delete cu.animationend.animation, delete cu.animationiteration.animation, delete cu.animationstart.animation), "TransitionEvent" in window || delete cu.transitionend.transition);
  function vc(n) {
    if (lr[n]) return lr[n];
    if (!cu[n]) return n;
    var r = cu[n], l;
    for (l in r) if (r.hasOwnProperty(l) && l in sd) return lr[n] = r[l];
    return n;
  }
  var Sv = vc("animationend"), Ev = vc("animationiteration"), Cv = vc("animationstart"), Rv = vc("transitionend"), cd = /* @__PURE__ */ new Map(), hc = "abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");
  function _a(n, r) {
    cd.set(n, r), Ee(r, [n]);
  }
  for (var fd = 0; fd < hc.length; fd++) {
    var fu = hc[fd], ty = fu.toLowerCase(), ny = fu[0].toUpperCase() + fu.slice(1);
    _a(ty, "on" + ny);
  }
  _a(Sv, "onAnimationEnd"), _a(Ev, "onAnimationIteration"), _a(Cv, "onAnimationStart"), _a("dblclick", "onDoubleClick"), _a("focusin", "onFocus"), _a("focusout", "onBlur"), _a(Rv, "onTransitionEnd"), S("onMouseEnter", ["mouseout", "mouseover"]), S("onMouseLeave", ["mouseout", "mouseover"]), S("onPointerEnter", ["pointerout", "pointerover"]), S("onPointerLeave", ["pointerout", "pointerover"]), Ee("onChange", "change click focusin focusout input keydown keyup selectionchange".split(" ")), Ee("onSelect", "focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")), Ee("onBeforeInput", ["compositionend", "keypress", "textInput", "paste"]), Ee("onCompositionEnd", "compositionend focusout keydown keypress keyup mousedown".split(" ")), Ee("onCompositionStart", "compositionstart focusout keydown keypress keyup mousedown".split(" ")), Ee("onCompositionUpdate", "compositionupdate focusout keydown keypress keyup mousedown".split(" "));
  var rs = "abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "), dd = new Set("cancel close invalid load scroll toggle".split(" ").concat(rs));
  function mc(n, r, l) {
    var o = n.type || "unknown-event";
    n.currentTarget = l, he(o, r, void 0, n), n.currentTarget = null;
  }
  function du(n, r) {
    r = (r & 4) !== 0;
    for (var l = 0; l < n.length; l++) {
      var o = n[l], c = o.event;
      o = o.listeners;
      e: {
        var d = void 0;
        if (r) for (var m = o.length - 1; 0 <= m; m--) {
          var E = o[m], T = E.instance, U = E.currentTarget;
          if (E = E.listener, T !== d && c.isPropagationStopped()) break e;
          mc(c, E, U), d = T;
        }
        else for (m = 0; m < o.length; m++) {
          if (E = o[m], T = E.instance, U = E.currentTarget, E = E.listener, T !== d && c.isPropagationStopped()) break e;
          mc(c, E, U), d = T;
        }
      }
    }
    if (vi) throw n = R, vi = !1, R = null, n;
  }
  function Vt(n, r) {
    var l = r[us];
    l === void 0 && (l = r[us] = /* @__PURE__ */ new Set());
    var o = n + "__bubble";
    l.has(o) || (Tv(r, n, 2, !1), l.add(o));
  }
  function yc(n, r, l) {
    var o = 0;
    r && (o |= 4), Tv(l, n, o, r);
  }
  var gc = "_reactListening" + Math.random().toString(36).slice(2);
  function oo(n) {
    if (!n[gc]) {
      n[gc] = !0, Te.forEach(function(l) {
        l !== "selectionchange" && (dd.has(l) || yc(l, !1, n), yc(l, !0, n));
      });
      var r = n.nodeType === 9 ? n : n.ownerDocument;
      r === null || r[gc] || (r[gc] = !0, yc("selectionchange", !1, r));
    }
  }
  function Tv(n, r, l, o) {
    switch (ro(r)) {
      case 1:
        var c = eo;
        break;
      case 4:
        c = to;
        break;
      default:
        c = Cl;
    }
    l = c.bind(null, r, l, n), c = void 0, !_r || r !== "touchstart" && r !== "touchmove" && r !== "wheel" || (c = !0), o ? c !== void 0 ? n.addEventListener(r, l, { capture: !0, passive: c }) : n.addEventListener(r, l, !0) : c !== void 0 ? n.addEventListener(r, l, { passive: c }) : n.addEventListener(r, l, !1);
  }
  function Sc(n, r, l, o, c) {
    var d = o;
    if (!(r & 1) && !(r & 2) && o !== null) e: for (; ; ) {
      if (o === null) return;
      var m = o.tag;
      if (m === 3 || m === 4) {
        var E = o.stateNode.containerInfo;
        if (E === c || E.nodeType === 8 && E.parentNode === c) break;
        if (m === 4) for (m = o.return; m !== null; ) {
          var T = m.tag;
          if ((T === 3 || T === 4) && (T = m.stateNode.containerInfo, T === c || T.nodeType === 8 && T.parentNode === c)) return;
          m = m.return;
        }
        for (; E !== null; ) {
          if (m = vu(E), m === null) return;
          if (T = m.tag, T === 5 || T === 6) {
            o = d = m;
            continue e;
          }
          E = E.parentNode;
        }
      }
      o = o.return;
    }
    tu(function() {
      var U = d, W = Yt(l), K = [];
      e: {
        var Q = cd.get(n);
        if (Q !== void 0) {
          var fe = mt, me = n;
          switch (n) {
            case "keypress":
              if (F(l) === 0) break e;
            case "keydown":
            case "keyup":
              fe = ed;
              break;
            case "focusin":
              me = "focus", fe = ou;
              break;
            case "focusout":
              me = "blur", fe = ou;
              break;
            case "beforeblur":
            case "afterblur":
              fe = ou;
              break;
            case "click":
              if (l.button === 2) break e;
            case "auxclick":
            case "dblclick":
            case "mousedown":
            case "mousemove":
            case "mouseup":
            case "mouseout":
            case "mouseover":
            case "contextmenu":
              fe = Rl;
              break;
            case "drag":
            case "dragend":
            case "dragenter":
            case "dragexit":
            case "dragleave":
            case "dragover":
            case "dragstart":
            case "drop":
              fe = Bi;
              break;
            case "touchcancel":
            case "touchend":
            case "touchmove":
            case "touchstart":
              fe = av;
              break;
            case Sv:
            case Ev:
            case Cv:
              fe = oc;
              break;
            case Rv:
              fe = Yi;
              break;
            case "scroll":
              fe = rn;
              break;
            case "wheel":
              fe = $i;
              break;
            case "copy":
            case "cut":
            case "paste":
              fe = ev;
              break;
            case "gotpointercapture":
            case "lostpointercapture":
            case "pointercancel":
            case "pointerdown":
            case "pointermove":
            case "pointerout":
            case "pointerover":
            case "pointerup":
              fe = rv;
          }
          var Ce = (r & 4) !== 0, kn = !Ce && n === "scroll", D = Ce ? Q !== null ? Q + "Capture" : null : Q;
          Ce = [];
          for (var x = U, M; x !== null; ) {
            M = x;
            var G = M.stateNode;
            if (M.tag === 5 && G !== null && (M = G, D !== null && (G = br(x, D), G != null && Ce.push(so(x, G, M)))), kn) break;
            x = x.return;
          }
          0 < Ce.length && (Q = new fe(Q, me, null, l, W), K.push({ event: Q, listeners: Ce }));
        }
      }
      if (!(r & 7)) {
        e: {
          if (Q = n === "mouseover" || n === "pointerover", fe = n === "mouseout" || n === "pointerout", Q && l !== tn && (me = l.relatedTarget || l.fromElement) && (vu(me) || me[Qi])) break e;
          if ((fe || Q) && (Q = W.window === W ? W : (Q = W.ownerDocument) ? Q.defaultView || Q.parentWindow : window, fe ? (me = l.relatedTarget || l.toElement, fe = U, me = me ? vu(me) : null, me !== null && (kn = Ze(me), me !== kn || me.tag !== 5 && me.tag !== 6) && (me = null)) : (fe = null, me = U), fe !== me)) {
            if (Ce = Rl, G = "onMouseLeave", D = "onMouseEnter", x = "mouse", (n === "pointerout" || n === "pointerover") && (Ce = rv, G = "onPointerLeave", D = "onPointerEnter", x = "pointer"), kn = fe == null ? Q : ni(fe), M = me == null ? Q : ni(me), Q = new Ce(G, x + "leave", fe, l, W), Q.target = kn, Q.relatedTarget = M, G = null, vu(W) === U && (Ce = new Ce(D, x + "enter", me, l, W), Ce.target = M, Ce.relatedTarget = kn, G = Ce), kn = G, fe && me) t: {
              for (Ce = fe, D = me, x = 0, M = Ce; M; M = wl(M)) x++;
              for (M = 0, G = D; G; G = wl(G)) M++;
              for (; 0 < x - M; ) Ce = wl(Ce), x--;
              for (; 0 < M - x; ) D = wl(D), M--;
              for (; x--; ) {
                if (Ce === D || D !== null && Ce === D.alternate) break t;
                Ce = wl(Ce), D = wl(D);
              }
              Ce = null;
            }
            else Ce = null;
            fe !== null && wv(K, Q, fe, Ce, !1), me !== null && kn !== null && wv(K, kn, me, Ce, !0);
          }
        }
        e: {
          if (Q = U ? ni(U) : window, fe = Q.nodeName && Q.nodeName.toLowerCase(), fe === "select" || fe === "input" && Q.type === "file") var ye = qm;
          else if (cv(Q)) if (dv) ye = yv;
          else {
            ye = mv;
            var Ue = Xm;
          }
          else (fe = Q.nodeName) && fe.toLowerCase() === "input" && (Q.type === "checkbox" || Q.type === "radio") && (ye = Zm);
          if (ye && (ye = ye(n, U))) {
            rd(K, ye, l, W);
            break e;
          }
          Ue && Ue(n, Q, U), n === "focusout" && (Ue = Q._wrapperState) && Ue.controlled && Q.type === "number" && oa(Q, "number", Q.value);
        }
        switch (Ue = U ? ni(U) : window, n) {
          case "focusin":
            (cv(Ue) || Ue.contentEditable === "true") && (uo = Ue, ld = U, ns = null);
            break;
          case "focusout":
            ns = ld = uo = null;
            break;
          case "mousedown":
            ud = !0;
            break;
          case "contextmenu":
          case "mouseup":
          case "dragend":
            ud = !1, od(K, l, W);
            break;
          case "selectionchange":
            if (ey) break;
          case "keydown":
          case "keyup":
            od(K, l, W);
        }
        var je;
        if (ao) e: {
          switch (n) {
            case "compositionstart":
              var $e = "onCompositionStart";
              break e;
            case "compositionend":
              $e = "onCompositionEnd";
              break e;
            case "compositionupdate":
              $e = "onCompositionUpdate";
              break e;
          }
          $e = void 0;
        }
        else io ? uv(n, l) && ($e = "onCompositionEnd") : n === "keydown" && l.keyCode === 229 && ($e = "onCompositionStart");
        $e && (iv && l.locale !== "ko" && (io || $e !== "onCompositionStart" ? $e === "onCompositionEnd" && io && (je = z()) : (ei = W, h = "value" in ei ? ei.value : ei.textContent, io = !0)), Ue = as(U, $e), 0 < Ue.length && ($e = new Xf($e, n, null, l, W), K.push({ event: $e, listeners: Ue }), je ? $e.data = je : (je = ov(l), je !== null && ($e.data = je)))), (je = Zo ? sv(n, l) : Gm(n, l)) && (U = as(U, "onBeforeInput"), 0 < U.length && (W = new Xf("onBeforeInput", "beforeinput", null, l, W), K.push({ event: W, listeners: U }), W.data = je));
      }
      du(K, r);
    });
  }
  function so(n, r, l) {
    return { instance: n, listener: r, currentTarget: l };
  }
  function as(n, r) {
    for (var l = r + "Capture", o = []; n !== null; ) {
      var c = n, d = c.stateNode;
      c.tag === 5 && d !== null && (c = d, d = br(n, l), d != null && o.unshift(so(n, d, c)), d = br(n, r), d != null && o.push(so(n, d, c))), n = n.return;
    }
    return o;
  }
  function wl(n) {
    if (n === null) return null;
    do
      n = n.return;
    while (n && n.tag !== 5);
    return n || null;
  }
  function wv(n, r, l, o, c) {
    for (var d = r._reactName, m = []; l !== null && l !== o; ) {
      var E = l, T = E.alternate, U = E.stateNode;
      if (T !== null && T === o) break;
      E.tag === 5 && U !== null && (E = U, c ? (T = br(l, d), T != null && m.unshift(so(l, T, E))) : c || (T = br(l, d), T != null && m.push(so(l, T, E)))), l = l.return;
    }
    m.length !== 0 && n.push({ event: r, listeners: m });
  }
  var xv = /\r\n?/g, ry = /\u0000|\uFFFD/g;
  function bv(n) {
    return (typeof n == "string" ? n : "" + n).replace(xv, `
`).replace(ry, "");
  }
  function Ec(n, r, l) {
    if (r = bv(r), bv(n) !== r && l) throw Error(k(425));
  }
  function xl() {
  }
  var is = null, pu = null;
  function Cc(n, r) {
    return n === "textarea" || n === "noscript" || typeof r.children == "string" || typeof r.children == "number" || typeof r.dangerouslySetInnerHTML == "object" && r.dangerouslySetInnerHTML !== null && r.dangerouslySetInnerHTML.__html != null;
  }
  var Rc = typeof setTimeout == "function" ? setTimeout : void 0, pd = typeof clearTimeout == "function" ? clearTimeout : void 0, _v = typeof Promise == "function" ? Promise : void 0, co = typeof queueMicrotask == "function" ? queueMicrotask : typeof _v < "u" ? function(n) {
    return _v.resolve(null).then(n).catch(Tc);
  } : Rc;
  function Tc(n) {
    setTimeout(function() {
      throw n;
    });
  }
  function fo(n, r) {
    var l = r, o = 0;
    do {
      var c = l.nextSibling;
      if (n.removeChild(l), c && c.nodeType === 8) if (l = c.data, l === "/$") {
        if (o === 0) {
          n.removeChild(c), Ja(r);
          return;
        }
        o--;
      } else l !== "$" && l !== "$?" && l !== "$!" || o++;
      l = c;
    } while (l);
    Ja(r);
  }
  function Ei(n) {
    for (; n != null; n = n.nextSibling) {
      var r = n.nodeType;
      if (r === 1 || r === 3) break;
      if (r === 8) {
        if (r = n.data, r === "$" || r === "$!" || r === "$?") break;
        if (r === "/$") return null;
      }
    }
    return n;
  }
  function kv(n) {
    n = n.previousSibling;
    for (var r = 0; n; ) {
      if (n.nodeType === 8) {
        var l = n.data;
        if (l === "$" || l === "$!" || l === "$?") {
          if (r === 0) return n;
          r--;
        } else l === "/$" && r++;
      }
      n = n.previousSibling;
    }
    return null;
  }
  var bl = Math.random().toString(36).slice(2), Ci = "__reactFiber$" + bl, ls = "__reactProps$" + bl, Qi = "__reactContainer$" + bl, us = "__reactEvents$" + bl, po = "__reactListeners$" + bl, ay = "__reactHandles$" + bl;
  function vu(n) {
    var r = n[Ci];
    if (r) return r;
    for (var l = n.parentNode; l; ) {
      if (r = l[Qi] || l[Ci]) {
        if (l = r.alternate, r.child !== null || l !== null && l.child !== null) for (n = kv(n); n !== null; ) {
          if (l = n[Ci]) return l;
          n = kv(n);
        }
        return r;
      }
      n = l, l = n.parentNode;
    }
    return null;
  }
  function De(n) {
    return n = n[Ci] || n[Qi], !n || n.tag !== 5 && n.tag !== 6 && n.tag !== 13 && n.tag !== 3 ? null : n;
  }
  function ni(n) {
    if (n.tag === 5 || n.tag === 6) return n.stateNode;
    throw Error(k(33));
  }
  function mn(n) {
    return n[ls] || null;
  }
  var Ct = [], ka = -1;
  function Da(n) {
    return { current: n };
  }
  function an(n) {
    0 > ka || (n.current = Ct[ka], Ct[ka] = null, ka--);
  }
  function _e(n, r) {
    ka++, Ct[ka] = n.current, n.current = r;
  }
  var Cr = {}, En = Da(Cr), $n = Da(!1), Wr = Cr;
  function Gr(n, r) {
    var l = n.type.contextTypes;
    if (!l) return Cr;
    var o = n.stateNode;
    if (o && o.__reactInternalMemoizedUnmaskedChildContext === r) return o.__reactInternalMemoizedMaskedChildContext;
    var c = {}, d;
    for (d in l) c[d] = r[d];
    return o && (n = n.stateNode, n.__reactInternalMemoizedUnmaskedChildContext = r, n.__reactInternalMemoizedMaskedChildContext = c), c;
  }
  function Nn(n) {
    return n = n.childContextTypes, n != null;
  }
  function vo() {
    an($n), an(En);
  }
  function Dv(n, r, l) {
    if (En.current !== Cr) throw Error(k(168));
    _e(En, r), _e($n, l);
  }
  function os(n, r, l) {
    var o = n.stateNode;
    if (r = r.childContextTypes, typeof o.getChildContext != "function") return l;
    o = o.getChildContext();
    for (var c in o) if (!(c in r)) throw Error(k(108, nt(n) || "Unknown", c));
    return ne({}, l, o);
  }
  function Xn(n) {
    return n = (n = n.stateNode) && n.__reactInternalMemoizedMergedChildContext || Cr, Wr = En.current, _e(En, n), _e($n, $n.current), !0;
  }
  function wc(n, r, l) {
    var o = n.stateNode;
    if (!o) throw Error(k(169));
    l ? (n = os(n, r, Wr), o.__reactInternalMemoizedMergedChildContext = n, an($n), an(En), _e(En, n)) : an($n), _e($n, l);
  }
  var Ri = null, ho = !1, Wi = !1;
  function xc(n) {
    Ri === null ? Ri = [n] : Ri.push(n);
  }
  function _l(n) {
    ho = !0, xc(n);
  }
  function Ti() {
    if (!Wi && Ri !== null) {
      Wi = !0;
      var n = 0, r = Lt;
      try {
        var l = Ri;
        for (Lt = 1; n < l.length; n++) {
          var o = l[n];
          do
            o = o(!0);
          while (o !== null);
        }
        Ri = null, ho = !1;
      } catch (c) {
        throw Ri !== null && (Ri = Ri.slice(n + 1)), sn(qa, Ti), c;
      } finally {
        Lt = r, Wi = !1;
      }
    }
    return null;
  }
  var kl = [], Dl = 0, Ol = null, Gi = 0, zn = [], Oa = 0, da = null, wi = 1, xi = "";
  function hu(n, r) {
    kl[Dl++] = Gi, kl[Dl++] = Ol, Ol = n, Gi = r;
  }
  function Ov(n, r, l) {
    zn[Oa++] = wi, zn[Oa++] = xi, zn[Oa++] = da, da = n;
    var o = wi;
    n = xi;
    var c = 32 - kr(o) - 1;
    o &= ~(1 << c), l += 1;
    var d = 32 - kr(r) + c;
    if (30 < d) {
      var m = c - c % 5;
      d = (o & (1 << m) - 1).toString(32), o >>= m, c -= m, wi = 1 << 32 - kr(r) + c | l << c | o, xi = d + n;
    } else wi = 1 << d | l << c | o, xi = n;
  }
  function bc(n) {
    n.return !== null && (hu(n, 1), Ov(n, 1, 0));
  }
  function _c(n) {
    for (; n === Ol; ) Ol = kl[--Dl], kl[Dl] = null, Gi = kl[--Dl], kl[Dl] = null;
    for (; n === da; ) da = zn[--Oa], zn[Oa] = null, xi = zn[--Oa], zn[Oa] = null, wi = zn[--Oa], zn[Oa] = null;
  }
  var Kr = null, qr = null, dn = !1, La = null;
  function vd(n, r) {
    var l = Aa(5, null, null, 0);
    l.elementType = "DELETED", l.stateNode = r, l.return = n, r = n.deletions, r === null ? (n.deletions = [l], n.flags |= 16) : r.push(l);
  }
  function Lv(n, r) {
    switch (n.tag) {
      case 5:
        var l = n.type;
        return r = r.nodeType !== 1 || l.toLowerCase() !== r.nodeName.toLowerCase() ? null : r, r !== null ? (n.stateNode = r, Kr = n, qr = Ei(r.firstChild), !0) : !1;
      case 6:
        return r = n.pendingProps === "" || r.nodeType !== 3 ? null : r, r !== null ? (n.stateNode = r, Kr = n, qr = null, !0) : !1;
      case 13:
        return r = r.nodeType !== 8 ? null : r, r !== null ? (l = da !== null ? { id: wi, overflow: xi } : null, n.memoizedState = { dehydrated: r, treeContext: l, retryLane: 1073741824 }, l = Aa(18, null, null, 0), l.stateNode = r, l.return = n, n.child = l, Kr = n, qr = null, !0) : !1;
      default:
        return !1;
    }
  }
  function hd(n) {
    return (n.mode & 1) !== 0 && (n.flags & 128) === 0;
  }
  function md(n) {
    if (dn) {
      var r = qr;
      if (r) {
        var l = r;
        if (!Lv(n, r)) {
          if (hd(n)) throw Error(k(418));
          r = Ei(l.nextSibling);
          var o = Kr;
          r && Lv(n, r) ? vd(o, l) : (n.flags = n.flags & -4097 | 2, dn = !1, Kr = n);
        }
      } else {
        if (hd(n)) throw Error(k(418));
        n.flags = n.flags & -4097 | 2, dn = !1, Kr = n;
      }
    }
  }
  function Qn(n) {
    for (n = n.return; n !== null && n.tag !== 5 && n.tag !== 3 && n.tag !== 13; ) n = n.return;
    Kr = n;
  }
  function kc(n) {
    if (n !== Kr) return !1;
    if (!dn) return Qn(n), dn = !0, !1;
    var r;
    if ((r = n.tag !== 3) && !(r = n.tag !== 5) && (r = n.type, r = r !== "head" && r !== "body" && !Cc(n.type, n.memoizedProps)), r && (r = qr)) {
      if (hd(n)) throw ss(), Error(k(418));
      for (; r; ) vd(n, r), r = Ei(r.nextSibling);
    }
    if (Qn(n), n.tag === 13) {
      if (n = n.memoizedState, n = n !== null ? n.dehydrated : null, !n) throw Error(k(317));
      e: {
        for (n = n.nextSibling, r = 0; n; ) {
          if (n.nodeType === 8) {
            var l = n.data;
            if (l === "/$") {
              if (r === 0) {
                qr = Ei(n.nextSibling);
                break e;
              }
              r--;
            } else l !== "$" && l !== "$!" && l !== "$?" || r++;
          }
          n = n.nextSibling;
        }
        qr = null;
      }
    } else qr = Kr ? Ei(n.stateNode.nextSibling) : null;
    return !0;
  }
  function ss() {
    for (var n = qr; n; ) n = Ei(n.nextSibling);
  }
  function Ll() {
    qr = Kr = null, dn = !1;
  }
  function Ki(n) {
    La === null ? La = [n] : La.push(n);
  }
  var iy = it.ReactCurrentBatchConfig;
  function mu(n, r, l) {
    if (n = l.ref, n !== null && typeof n != "function" && typeof n != "object") {
      if (l._owner) {
        if (l = l._owner, l) {
          if (l.tag !== 1) throw Error(k(309));
          var o = l.stateNode;
        }
        if (!o) throw Error(k(147, n));
        var c = o, d = "" + n;
        return r !== null && r.ref !== null && typeof r.ref == "function" && r.ref._stringRef === d ? r.ref : (r = function(m) {
          var E = c.refs;
          m === null ? delete E[d] : E[d] = m;
        }, r._stringRef = d, r);
      }
      if (typeof n != "string") throw Error(k(284));
      if (!l._owner) throw Error(k(290, n));
    }
    return n;
  }
  function Dc(n, r) {
    throw n = Object.prototype.toString.call(r), Error(k(31, n === "[object Object]" ? "object with keys {" + Object.keys(r).join(", ") + "}" : n));
  }
  function Mv(n) {
    var r = n._init;
    return r(n._payload);
  }
  function yu(n) {
    function r(D, x) {
      if (n) {
        var M = D.deletions;
        M === null ? (D.deletions = [x], D.flags |= 16) : M.push(x);
      }
    }
    function l(D, x) {
      if (!n) return null;
      for (; x !== null; ) r(D, x), x = x.sibling;
      return null;
    }
    function o(D, x) {
      for (D = /* @__PURE__ */ new Map(); x !== null; ) x.key !== null ? D.set(x.key, x) : D.set(x.index, x), x = x.sibling;
      return D;
    }
    function c(D, x) {
      return D = Hl(D, x), D.index = 0, D.sibling = null, D;
    }
    function d(D, x, M) {
      return D.index = M, n ? (M = D.alternate, M !== null ? (M = M.index, M < x ? (D.flags |= 2, x) : M) : (D.flags |= 2, x)) : (D.flags |= 1048576, x);
    }
    function m(D) {
      return n && D.alternate === null && (D.flags |= 2), D;
    }
    function E(D, x, M, G) {
      return x === null || x.tag !== 6 ? (x = Wd(M, D.mode, G), x.return = D, x) : (x = c(x, M), x.return = D, x);
    }
    function T(D, x, M, G) {
      var ye = M.type;
      return ye === He ? W(D, x, M.props.children, G, M.key) : x !== null && (x.elementType === ye || typeof ye == "object" && ye !== null && ye.$$typeof === Ot && Mv(ye) === x.type) ? (G = c(x, M.props), G.ref = mu(D, x, M), G.return = D, G) : (G = Hs(M.type, M.key, M.props, null, D.mode, G), G.ref = mu(D, x, M), G.return = D, G);
    }
    function U(D, x, M, G) {
      return x === null || x.tag !== 4 || x.stateNode.containerInfo !== M.containerInfo || x.stateNode.implementation !== M.implementation ? (x = sf(M, D.mode, G), x.return = D, x) : (x = c(x, M.children || []), x.return = D, x);
    }
    function W(D, x, M, G, ye) {
      return x === null || x.tag !== 7 ? (x = tl(M, D.mode, G, ye), x.return = D, x) : (x = c(x, M), x.return = D, x);
    }
    function K(D, x, M) {
      if (typeof x == "string" && x !== "" || typeof x == "number") return x = Wd("" + x, D.mode, M), x.return = D, x;
      if (typeof x == "object" && x !== null) {
        switch (x.$$typeof) {
          case ke:
            return M = Hs(x.type, x.key, x.props, null, D.mode, M), M.ref = mu(D, null, x), M.return = D, M;
          case Qe:
            return x = sf(x, D.mode, M), x.return = D, x;
          case Ot:
            var G = x._init;
            return K(D, G(x._payload), M);
        }
        if (Kn(x) || we(x)) return x = tl(x, D.mode, M, null), x.return = D, x;
        Dc(D, x);
      }
      return null;
    }
    function Q(D, x, M, G) {
      var ye = x !== null ? x.key : null;
      if (typeof M == "string" && M !== "" || typeof M == "number") return ye !== null ? null : E(D, x, "" + M, G);
      if (typeof M == "object" && M !== null) {
        switch (M.$$typeof) {
          case ke:
            return M.key === ye ? T(D, x, M, G) : null;
          case Qe:
            return M.key === ye ? U(D, x, M, G) : null;
          case Ot:
            return ye = M._init, Q(
              D,
              x,
              ye(M._payload),
              G
            );
        }
        if (Kn(M) || we(M)) return ye !== null ? null : W(D, x, M, G, null);
        Dc(D, M);
      }
      return null;
    }
    function fe(D, x, M, G, ye) {
      if (typeof G == "string" && G !== "" || typeof G == "number") return D = D.get(M) || null, E(x, D, "" + G, ye);
      if (typeof G == "object" && G !== null) {
        switch (G.$$typeof) {
          case ke:
            return D = D.get(G.key === null ? M : G.key) || null, T(x, D, G, ye);
          case Qe:
            return D = D.get(G.key === null ? M : G.key) || null, U(x, D, G, ye);
          case Ot:
            var Ue = G._init;
            return fe(D, x, M, Ue(G._payload), ye);
        }
        if (Kn(G) || we(G)) return D = D.get(M) || null, W(x, D, G, ye, null);
        Dc(x, G);
      }
      return null;
    }
    function me(D, x, M, G) {
      for (var ye = null, Ue = null, je = x, $e = x = 0, er = null; je !== null && $e < M.length; $e++) {
        je.index > $e ? (er = je, je = null) : er = je.sibling;
        var zt = Q(D, je, M[$e], G);
        if (zt === null) {
          je === null && (je = er);
          break;
        }
        n && je && zt.alternate === null && r(D, je), x = d(zt, x, $e), Ue === null ? ye = zt : Ue.sibling = zt, Ue = zt, je = er;
      }
      if ($e === M.length) return l(D, je), dn && hu(D, $e), ye;
      if (je === null) {
        for (; $e < M.length; $e++) je = K(D, M[$e], G), je !== null && (x = d(je, x, $e), Ue === null ? ye = je : Ue.sibling = je, Ue = je);
        return dn && hu(D, $e), ye;
      }
      for (je = o(D, je); $e < M.length; $e++) er = fe(je, D, $e, M[$e], G), er !== null && (n && er.alternate !== null && je.delete(er.key === null ? $e : er.key), x = d(er, x, $e), Ue === null ? ye = er : Ue.sibling = er, Ue = er);
      return n && je.forEach(function(Bl) {
        return r(D, Bl);
      }), dn && hu(D, $e), ye;
    }
    function Ce(D, x, M, G) {
      var ye = we(M);
      if (typeof ye != "function") throw Error(k(150));
      if (M = ye.call(M), M == null) throw Error(k(151));
      for (var Ue = ye = null, je = x, $e = x = 0, er = null, zt = M.next(); je !== null && !zt.done; $e++, zt = M.next()) {
        je.index > $e ? (er = je, je = null) : er = je.sibling;
        var Bl = Q(D, je, zt.value, G);
        if (Bl === null) {
          je === null && (je = er);
          break;
        }
        n && je && Bl.alternate === null && r(D, je), x = d(Bl, x, $e), Ue === null ? ye = Bl : Ue.sibling = Bl, Ue = Bl, je = er;
      }
      if (zt.done) return l(
        D,
        je
      ), dn && hu(D, $e), ye;
      if (je === null) {
        for (; !zt.done; $e++, zt = M.next()) zt = K(D, zt.value, G), zt !== null && (x = d(zt, x, $e), Ue === null ? ye = zt : Ue.sibling = zt, Ue = zt);
        return dn && hu(D, $e), ye;
      }
      for (je = o(D, je); !zt.done; $e++, zt = M.next()) zt = fe(je, D, $e, zt.value, G), zt !== null && (n && zt.alternate !== null && je.delete(zt.key === null ? $e : zt.key), x = d(zt, x, $e), Ue === null ? ye = zt : Ue.sibling = zt, Ue = zt);
      return n && je.forEach(function(vh) {
        return r(D, vh);
      }), dn && hu(D, $e), ye;
    }
    function kn(D, x, M, G) {
      if (typeof M == "object" && M !== null && M.type === He && M.key === null && (M = M.props.children), typeof M == "object" && M !== null) {
        switch (M.$$typeof) {
          case ke:
            e: {
              for (var ye = M.key, Ue = x; Ue !== null; ) {
                if (Ue.key === ye) {
                  if (ye = M.type, ye === He) {
                    if (Ue.tag === 7) {
                      l(D, Ue.sibling), x = c(Ue, M.props.children), x.return = D, D = x;
                      break e;
                    }
                  } else if (Ue.elementType === ye || typeof ye == "object" && ye !== null && ye.$$typeof === Ot && Mv(ye) === Ue.type) {
                    l(D, Ue.sibling), x = c(Ue, M.props), x.ref = mu(D, Ue, M), x.return = D, D = x;
                    break e;
                  }
                  l(D, Ue);
                  break;
                } else r(D, Ue);
                Ue = Ue.sibling;
              }
              M.type === He ? (x = tl(M.props.children, D.mode, G, M.key), x.return = D, D = x) : (G = Hs(M.type, M.key, M.props, null, D.mode, G), G.ref = mu(D, x, M), G.return = D, D = G);
            }
            return m(D);
          case Qe:
            e: {
              for (Ue = M.key; x !== null; ) {
                if (x.key === Ue) if (x.tag === 4 && x.stateNode.containerInfo === M.containerInfo && x.stateNode.implementation === M.implementation) {
                  l(D, x.sibling), x = c(x, M.children || []), x.return = D, D = x;
                  break e;
                } else {
                  l(D, x);
                  break;
                }
                else r(D, x);
                x = x.sibling;
              }
              x = sf(M, D.mode, G), x.return = D, D = x;
            }
            return m(D);
          case Ot:
            return Ue = M._init, kn(D, x, Ue(M._payload), G);
        }
        if (Kn(M)) return me(D, x, M, G);
        if (we(M)) return Ce(D, x, M, G);
        Dc(D, M);
      }
      return typeof M == "string" && M !== "" || typeof M == "number" ? (M = "" + M, x !== null && x.tag === 6 ? (l(D, x.sibling), x = c(x, M), x.return = D, D = x) : (l(D, x), x = Wd(M, D.mode, G), x.return = D, D = x), m(D)) : l(D, x);
    }
    return kn;
  }
  var wn = yu(!0), le = yu(!1), pa = Da(null), Xr = null, mo = null, yd = null;
  function gd() {
    yd = mo = Xr = null;
  }
  function Sd(n) {
    var r = pa.current;
    an(pa), n._currentValue = r;
  }
  function Ed(n, r, l) {
    for (; n !== null; ) {
      var o = n.alternate;
      if ((n.childLanes & r) !== r ? (n.childLanes |= r, o !== null && (o.childLanes |= r)) : o !== null && (o.childLanes & r) !== r && (o.childLanes |= r), n === l) break;
      n = n.return;
    }
  }
  function yn(n, r) {
    Xr = n, yd = mo = null, n = n.dependencies, n !== null && n.firstContext !== null && (n.lanes & r && (An = !0), n.firstContext = null);
  }
  function Ma(n) {
    var r = n._currentValue;
    if (yd !== n) if (n = { context: n, memoizedValue: r, next: null }, mo === null) {
      if (Xr === null) throw Error(k(308));
      mo = n, Xr.dependencies = { lanes: 0, firstContext: n };
    } else mo = mo.next = n;
    return r;
  }
  var gu = null;
  function Cd(n) {
    gu === null ? gu = [n] : gu.push(n);
  }
  function Rd(n, r, l, o) {
    var c = r.interleaved;
    return c === null ? (l.next = l, Cd(r)) : (l.next = c.next, c.next = l), r.interleaved = l, va(n, o);
  }
  function va(n, r) {
    n.lanes |= r;
    var l = n.alternate;
    for (l !== null && (l.lanes |= r), l = n, n = n.return; n !== null; ) n.childLanes |= r, l = n.alternate, l !== null && (l.childLanes |= r), l = n, n = n.return;
    return l.tag === 3 ? l.stateNode : null;
  }
  var ha = !1;
  function Td(n) {
    n.updateQueue = { baseState: n.memoizedState, firstBaseUpdate: null, lastBaseUpdate: null, shared: { pending: null, interleaved: null, lanes: 0 }, effects: null };
  }
  function Nv(n, r) {
    n = n.updateQueue, r.updateQueue === n && (r.updateQueue = { baseState: n.baseState, firstBaseUpdate: n.firstBaseUpdate, lastBaseUpdate: n.lastBaseUpdate, shared: n.shared, effects: n.effects });
  }
  function qi(n, r) {
    return { eventTime: n, lane: r, tag: 0, payload: null, callback: null, next: null };
  }
  function Ml(n, r, l) {
    var o = n.updateQueue;
    if (o === null) return null;
    if (o = o.shared, Rt & 2) {
      var c = o.pending;
      return c === null ? r.next = r : (r.next = c.next, c.next = r), o.pending = r, va(n, l);
    }
    return c = o.interleaved, c === null ? (r.next = r, Cd(o)) : (r.next = c.next, c.next = r), o.interleaved = r, va(n, l);
  }
  function Oc(n, r, l) {
    if (r = r.updateQueue, r !== null && (r = r.shared, (l & 4194240) !== 0)) {
      var o = r.lanes;
      o &= n.pendingLanes, l |= o, r.lanes = l, Vi(n, l);
    }
  }
  function zv(n, r) {
    var l = n.updateQueue, o = n.alternate;
    if (o !== null && (o = o.updateQueue, l === o)) {
      var c = null, d = null;
      if (l = l.firstBaseUpdate, l !== null) {
        do {
          var m = { eventTime: l.eventTime, lane: l.lane, tag: l.tag, payload: l.payload, callback: l.callback, next: null };
          d === null ? c = d = m : d = d.next = m, l = l.next;
        } while (l !== null);
        d === null ? c = d = r : d = d.next = r;
      } else c = d = r;
      l = { baseState: o.baseState, firstBaseUpdate: c, lastBaseUpdate: d, shared: o.shared, effects: o.effects }, n.updateQueue = l;
      return;
    }
    n = l.lastBaseUpdate, n === null ? l.firstBaseUpdate = r : n.next = r, l.lastBaseUpdate = r;
  }
  function cs(n, r, l, o) {
    var c = n.updateQueue;
    ha = !1;
    var d = c.firstBaseUpdate, m = c.lastBaseUpdate, E = c.shared.pending;
    if (E !== null) {
      c.shared.pending = null;
      var T = E, U = T.next;
      T.next = null, m === null ? d = U : m.next = U, m = T;
      var W = n.alternate;
      W !== null && (W = W.updateQueue, E = W.lastBaseUpdate, E !== m && (E === null ? W.firstBaseUpdate = U : E.next = U, W.lastBaseUpdate = T));
    }
    if (d !== null) {
      var K = c.baseState;
      m = 0, W = U = T = null, E = d;
      do {
        var Q = E.lane, fe = E.eventTime;
        if ((o & Q) === Q) {
          W !== null && (W = W.next = {
            eventTime: fe,
            lane: 0,
            tag: E.tag,
            payload: E.payload,
            callback: E.callback,
            next: null
          });
          e: {
            var me = n, Ce = E;
            switch (Q = r, fe = l, Ce.tag) {
              case 1:
                if (me = Ce.payload, typeof me == "function") {
                  K = me.call(fe, K, Q);
                  break e;
                }
                K = me;
                break e;
              case 3:
                me.flags = me.flags & -65537 | 128;
              case 0:
                if (me = Ce.payload, Q = typeof me == "function" ? me.call(fe, K, Q) : me, Q == null) break e;
                K = ne({}, K, Q);
                break e;
              case 2:
                ha = !0;
            }
          }
          E.callback !== null && E.lane !== 0 && (n.flags |= 64, Q = c.effects, Q === null ? c.effects = [E] : Q.push(E));
        } else fe = { eventTime: fe, lane: Q, tag: E.tag, payload: E.payload, callback: E.callback, next: null }, W === null ? (U = W = fe, T = K) : W = W.next = fe, m |= Q;
        if (E = E.next, E === null) {
          if (E = c.shared.pending, E === null) break;
          Q = E, E = Q.next, Q.next = null, c.lastBaseUpdate = Q, c.shared.pending = null;
        }
      } while (!0);
      if (W === null && (T = K), c.baseState = T, c.firstBaseUpdate = U, c.lastBaseUpdate = W, r = c.shared.interleaved, r !== null) {
        c = r;
        do
          m |= c.lane, c = c.next;
        while (c !== r);
      } else d === null && (c.shared.lanes = 0);
      Oi |= m, n.lanes = m, n.memoizedState = K;
    }
  }
  function wd(n, r, l) {
    if (n = r.effects, r.effects = null, n !== null) for (r = 0; r < n.length; r++) {
      var o = n[r], c = o.callback;
      if (c !== null) {
        if (o.callback = null, o = l, typeof c != "function") throw Error(k(191, c));
        c.call(o);
      }
    }
  }
  var fs = {}, bi = Da(fs), ds = Da(fs), ps = Da(fs);
  function Su(n) {
    if (n === fs) throw Error(k(174));
    return n;
  }
  function xd(n, r) {
    switch (_e(ps, r), _e(ds, n), _e(bi, fs), n = r.nodeType, n) {
      case 9:
      case 11:
        r = (r = r.documentElement) ? r.namespaceURI : sa(null, "");
        break;
      default:
        n = n === 8 ? r.parentNode : r, r = n.namespaceURI || null, n = n.tagName, r = sa(r, n);
    }
    an(bi), _e(bi, r);
  }
  function Eu() {
    an(bi), an(ds), an(ps);
  }
  function Uv(n) {
    Su(ps.current);
    var r = Su(bi.current), l = sa(r, n.type);
    r !== l && (_e(ds, n), _e(bi, l));
  }
  function Lc(n) {
    ds.current === n && (an(bi), an(ds));
  }
  var gn = Da(0);
  function Mc(n) {
    for (var r = n; r !== null; ) {
      if (r.tag === 13) {
        var l = r.memoizedState;
        if (l !== null && (l = l.dehydrated, l === null || l.data === "$?" || l.data === "$!")) return r;
      } else if (r.tag === 19 && r.memoizedProps.revealOrder !== void 0) {
        if (r.flags & 128) return r;
      } else if (r.child !== null) {
        r.child.return = r, r = r.child;
        continue;
      }
      if (r === n) break;
      for (; r.sibling === null; ) {
        if (r.return === null || r.return === n) return null;
        r = r.return;
      }
      r.sibling.return = r.return, r = r.sibling;
    }
    return null;
  }
  var vs = [];
  function Oe() {
    for (var n = 0; n < vs.length; n++) vs[n]._workInProgressVersionPrimary = null;
    vs.length = 0;
  }
  var vt = it.ReactCurrentDispatcher, Mt = it.ReactCurrentBatchConfig, Kt = 0, Nt = null, Un = null, Zn = null, Nc = !1, hs = !1, Cu = 0, $ = 0;
  function Dt() {
    throw Error(k(321));
  }
  function Be(n, r) {
    if (r === null) return !1;
    for (var l = 0; l < r.length && l < n.length; l++) if (!ti(n[l], r[l])) return !1;
    return !0;
  }
  function Nl(n, r, l, o, c, d) {
    if (Kt = d, Nt = r, r.memoizedState = null, r.updateQueue = null, r.lanes = 0, vt.current = n === null || n.memoizedState === null ? Gc : Cs, n = l(o, c), hs) {
      d = 0;
      do {
        if (hs = !1, Cu = 0, 25 <= d) throw Error(k(301));
        d += 1, Zn = Un = null, r.updateQueue = null, vt.current = Kc, n = l(o, c);
      } while (hs);
    }
    if (vt.current = bu, r = Un !== null && Un.next !== null, Kt = 0, Zn = Un = Nt = null, Nc = !1, r) throw Error(k(300));
    return n;
  }
  function ri() {
    var n = Cu !== 0;
    return Cu = 0, n;
  }
  function Rr() {
    var n = { memoizedState: null, baseState: null, baseQueue: null, queue: null, next: null };
    return Zn === null ? Nt.memoizedState = Zn = n : Zn = Zn.next = n, Zn;
  }
  function xn() {
    if (Un === null) {
      var n = Nt.alternate;
      n = n !== null ? n.memoizedState : null;
    } else n = Un.next;
    var r = Zn === null ? Nt.memoizedState : Zn.next;
    if (r !== null) Zn = r, Un = n;
    else {
      if (n === null) throw Error(k(310));
      Un = n, n = { memoizedState: Un.memoizedState, baseState: Un.baseState, baseQueue: Un.baseQueue, queue: Un.queue, next: null }, Zn === null ? Nt.memoizedState = Zn = n : Zn = Zn.next = n;
    }
    return Zn;
  }
  function Xi(n, r) {
    return typeof r == "function" ? r(n) : r;
  }
  function zl(n) {
    var r = xn(), l = r.queue;
    if (l === null) throw Error(k(311));
    l.lastRenderedReducer = n;
    var o = Un, c = o.baseQueue, d = l.pending;
    if (d !== null) {
      if (c !== null) {
        var m = c.next;
        c.next = d.next, d.next = m;
      }
      o.baseQueue = c = d, l.pending = null;
    }
    if (c !== null) {
      d = c.next, o = o.baseState;
      var E = m = null, T = null, U = d;
      do {
        var W = U.lane;
        if ((Kt & W) === W) T !== null && (T = T.next = { lane: 0, action: U.action, hasEagerState: U.hasEagerState, eagerState: U.eagerState, next: null }), o = U.hasEagerState ? U.eagerState : n(o, U.action);
        else {
          var K = {
            lane: W,
            action: U.action,
            hasEagerState: U.hasEagerState,
            eagerState: U.eagerState,
            next: null
          };
          T === null ? (E = T = K, m = o) : T = T.next = K, Nt.lanes |= W, Oi |= W;
        }
        U = U.next;
      } while (U !== null && U !== d);
      T === null ? m = o : T.next = E, ti(o, r.memoizedState) || (An = !0), r.memoizedState = o, r.baseState = m, r.baseQueue = T, l.lastRenderedState = o;
    }
    if (n = l.interleaved, n !== null) {
      c = n;
      do
        d = c.lane, Nt.lanes |= d, Oi |= d, c = c.next;
      while (c !== n);
    } else c === null && (l.lanes = 0);
    return [r.memoizedState, l.dispatch];
  }
  function Ru(n) {
    var r = xn(), l = r.queue;
    if (l === null) throw Error(k(311));
    l.lastRenderedReducer = n;
    var o = l.dispatch, c = l.pending, d = r.memoizedState;
    if (c !== null) {
      l.pending = null;
      var m = c = c.next;
      do
        d = n(d, m.action), m = m.next;
      while (m !== c);
      ti(d, r.memoizedState) || (An = !0), r.memoizedState = d, r.baseQueue === null && (r.baseState = d), l.lastRenderedState = d;
    }
    return [d, o];
  }
  function zc() {
  }
  function Uc(n, r) {
    var l = Nt, o = xn(), c = r(), d = !ti(o.memoizedState, c);
    if (d && (o.memoizedState = c, An = !0), o = o.queue, ms(Fc.bind(null, l, o, n), [n]), o.getSnapshot !== r || d || Zn !== null && Zn.memoizedState.tag & 1) {
      if (l.flags |= 2048, Tu(9, jc.bind(null, l, o, c, r), void 0, null), Wn === null) throw Error(k(349));
      Kt & 30 || Ac(l, r, c);
    }
    return c;
  }
  function Ac(n, r, l) {
    n.flags |= 16384, n = { getSnapshot: r, value: l }, r = Nt.updateQueue, r === null ? (r = { lastEffect: null, stores: null }, Nt.updateQueue = r, r.stores = [n]) : (l = r.stores, l === null ? r.stores = [n] : l.push(n));
  }
  function jc(n, r, l, o) {
    r.value = l, r.getSnapshot = o, Hc(r) && Pc(n);
  }
  function Fc(n, r, l) {
    return l(function() {
      Hc(r) && Pc(n);
    });
  }
  function Hc(n) {
    var r = n.getSnapshot;
    n = n.value;
    try {
      var l = r();
      return !ti(n, l);
    } catch {
      return !0;
    }
  }
  function Pc(n) {
    var r = va(n, 1);
    r !== null && zr(r, n, 1, -1);
  }
  function Vc(n) {
    var r = Rr();
    return typeof n == "function" && (n = n()), r.memoizedState = r.baseState = n, n = { pending: null, interleaved: null, lanes: 0, dispatch: null, lastRenderedReducer: Xi, lastRenderedState: n }, r.queue = n, n = n.dispatch = xu.bind(null, Nt, n), [r.memoizedState, n];
  }
  function Tu(n, r, l, o) {
    return n = { tag: n, create: r, destroy: l, deps: o, next: null }, r = Nt.updateQueue, r === null ? (r = { lastEffect: null, stores: null }, Nt.updateQueue = r, r.lastEffect = n.next = n) : (l = r.lastEffect, l === null ? r.lastEffect = n.next = n : (o = l.next, l.next = n, n.next = o, r.lastEffect = n)), n;
  }
  function Bc() {
    return xn().memoizedState;
  }
  function yo(n, r, l, o) {
    var c = Rr();
    Nt.flags |= n, c.memoizedState = Tu(1 | r, l, void 0, o === void 0 ? null : o);
  }
  function go(n, r, l, o) {
    var c = xn();
    o = o === void 0 ? null : o;
    var d = void 0;
    if (Un !== null) {
      var m = Un.memoizedState;
      if (d = m.destroy, o !== null && Be(o, m.deps)) {
        c.memoizedState = Tu(r, l, d, o);
        return;
      }
    }
    Nt.flags |= n, c.memoizedState = Tu(1 | r, l, d, o);
  }
  function Ic(n, r) {
    return yo(8390656, 8, n, r);
  }
  function ms(n, r) {
    return go(2048, 8, n, r);
  }
  function Yc(n, r) {
    return go(4, 2, n, r);
  }
  function ys(n, r) {
    return go(4, 4, n, r);
  }
  function wu(n, r) {
    if (typeof r == "function") return n = n(), r(n), function() {
      r(null);
    };
    if (r != null) return n = n(), r.current = n, function() {
      r.current = null;
    };
  }
  function $c(n, r, l) {
    return l = l != null ? l.concat([n]) : null, go(4, 4, wu.bind(null, r, n), l);
  }
  function gs() {
  }
  function Qc(n, r) {
    var l = xn();
    r = r === void 0 ? null : r;
    var o = l.memoizedState;
    return o !== null && r !== null && Be(r, o[1]) ? o[0] : (l.memoizedState = [n, r], n);
  }
  function Wc(n, r) {
    var l = xn();
    r = r === void 0 ? null : r;
    var o = l.memoizedState;
    return o !== null && r !== null && Be(r, o[1]) ? o[0] : (n = n(), l.memoizedState = [n, r], n);
  }
  function bd(n, r, l) {
    return Kt & 21 ? (ti(l, r) || (l = qu(), Nt.lanes |= l, Oi |= l, n.baseState = !0), r) : (n.baseState && (n.baseState = !1, An = !0), n.memoizedState = l);
  }
  function Ss(n, r) {
    var l = Lt;
    Lt = l !== 0 && 4 > l ? l : 4, n(!0);
    var o = Mt.transition;
    Mt.transition = {};
    try {
      n(!1), r();
    } finally {
      Lt = l, Mt.transition = o;
    }
  }
  function _d() {
    return xn().memoizedState;
  }
  function Es(n, r, l) {
    var o = Li(n);
    if (l = { lane: o, action: l, hasEagerState: !1, eagerState: null, next: null }, Zr(n)) Av(r, l);
    else if (l = Rd(n, r, l, o), l !== null) {
      var c = Hn();
      zr(l, n, o, c), Zt(l, r, o);
    }
  }
  function xu(n, r, l) {
    var o = Li(n), c = { lane: o, action: l, hasEagerState: !1, eagerState: null, next: null };
    if (Zr(n)) Av(r, c);
    else {
      var d = n.alternate;
      if (n.lanes === 0 && (d === null || d.lanes === 0) && (d = r.lastRenderedReducer, d !== null)) try {
        var m = r.lastRenderedState, E = d(m, l);
        if (c.hasEagerState = !0, c.eagerState = E, ti(E, m)) {
          var T = r.interleaved;
          T === null ? (c.next = c, Cd(r)) : (c.next = T.next, T.next = c), r.interleaved = c;
          return;
        }
      } catch {
      } finally {
      }
      l = Rd(n, r, c, o), l !== null && (c = Hn(), zr(l, n, o, c), Zt(l, r, o));
    }
  }
  function Zr(n) {
    var r = n.alternate;
    return n === Nt || r !== null && r === Nt;
  }
  function Av(n, r) {
    hs = Nc = !0;
    var l = n.pending;
    l === null ? r.next = r : (r.next = l.next, l.next = r), n.pending = r;
  }
  function Zt(n, r, l) {
    if (l & 4194240) {
      var o = r.lanes;
      o &= n.pendingLanes, l |= o, r.lanes = l, Vi(n, l);
    }
  }
  var bu = { readContext: Ma, useCallback: Dt, useContext: Dt, useEffect: Dt, useImperativeHandle: Dt, useInsertionEffect: Dt, useLayoutEffect: Dt, useMemo: Dt, useReducer: Dt, useRef: Dt, useState: Dt, useDebugValue: Dt, useDeferredValue: Dt, useTransition: Dt, useMutableSource: Dt, useSyncExternalStore: Dt, useId: Dt, unstable_isNewReconciler: !1 }, Gc = { readContext: Ma, useCallback: function(n, r) {
    return Rr().memoizedState = [n, r === void 0 ? null : r], n;
  }, useContext: Ma, useEffect: Ic, useImperativeHandle: function(n, r, l) {
    return l = l != null ? l.concat([n]) : null, yo(
      4194308,
      4,
      wu.bind(null, r, n),
      l
    );
  }, useLayoutEffect: function(n, r) {
    return yo(4194308, 4, n, r);
  }, useInsertionEffect: function(n, r) {
    return yo(4, 2, n, r);
  }, useMemo: function(n, r) {
    var l = Rr();
    return r = r === void 0 ? null : r, n = n(), l.memoizedState = [n, r], n;
  }, useReducer: function(n, r, l) {
    var o = Rr();
    return r = l !== void 0 ? l(r) : r, o.memoizedState = o.baseState = r, n = { pending: null, interleaved: null, lanes: 0, dispatch: null, lastRenderedReducer: n, lastRenderedState: r }, o.queue = n, n = n.dispatch = Es.bind(null, Nt, n), [o.memoizedState, n];
  }, useRef: function(n) {
    var r = Rr();
    return n = { current: n }, r.memoizedState = n;
  }, useState: Vc, useDebugValue: gs, useDeferredValue: function(n) {
    return Rr().memoizedState = n;
  }, useTransition: function() {
    var n = Vc(!1), r = n[0];
    return n = Ss.bind(null, n[1]), Rr().memoizedState = n, [r, n];
  }, useMutableSource: function() {
  }, useSyncExternalStore: function(n, r, l) {
    var o = Nt, c = Rr();
    if (dn) {
      if (l === void 0) throw Error(k(407));
      l = l();
    } else {
      if (l = r(), Wn === null) throw Error(k(349));
      Kt & 30 || Ac(o, r, l);
    }
    c.memoizedState = l;
    var d = { value: l, getSnapshot: r };
    return c.queue = d, Ic(Fc.bind(
      null,
      o,
      d,
      n
    ), [n]), o.flags |= 2048, Tu(9, jc.bind(null, o, d, l, r), void 0, null), l;
  }, useId: function() {
    var n = Rr(), r = Wn.identifierPrefix;
    if (dn) {
      var l = xi, o = wi;
      l = (o & ~(1 << 32 - kr(o) - 1)).toString(32) + l, r = ":" + r + "R" + l, l = Cu++, 0 < l && (r += "H" + l.toString(32)), r += ":";
    } else l = $++, r = ":" + r + "r" + l.toString(32) + ":";
    return n.memoizedState = r;
  }, unstable_isNewReconciler: !1 }, Cs = {
    readContext: Ma,
    useCallback: Qc,
    useContext: Ma,
    useEffect: ms,
    useImperativeHandle: $c,
    useInsertionEffect: Yc,
    useLayoutEffect: ys,
    useMemo: Wc,
    useReducer: zl,
    useRef: Bc,
    useState: function() {
      return zl(Xi);
    },
    useDebugValue: gs,
    useDeferredValue: function(n) {
      var r = xn();
      return bd(r, Un.memoizedState, n);
    },
    useTransition: function() {
      var n = zl(Xi)[0], r = xn().memoizedState;
      return [n, r];
    },
    useMutableSource: zc,
    useSyncExternalStore: Uc,
    useId: _d,
    unstable_isNewReconciler: !1
  }, Kc = { readContext: Ma, useCallback: Qc, useContext: Ma, useEffect: ms, useImperativeHandle: $c, useInsertionEffect: Yc, useLayoutEffect: ys, useMemo: Wc, useReducer: Ru, useRef: Bc, useState: function() {
    return Ru(Xi);
  }, useDebugValue: gs, useDeferredValue: function(n) {
    var r = xn();
    return Un === null ? r.memoizedState = n : bd(r, Un.memoizedState, n);
  }, useTransition: function() {
    var n = Ru(Xi)[0], r = xn().memoizedState;
    return [n, r];
  }, useMutableSource: zc, useSyncExternalStore: Uc, useId: _d, unstable_isNewReconciler: !1 };
  function ai(n, r) {
    if (n && n.defaultProps) {
      r = ne({}, r), n = n.defaultProps;
      for (var l in n) r[l] === void 0 && (r[l] = n[l]);
      return r;
    }
    return r;
  }
  function kd(n, r, l, o) {
    r = n.memoizedState, l = l(o, r), l = l == null ? r : ne({}, r, l), n.memoizedState = l, n.lanes === 0 && (n.updateQueue.baseState = l);
  }
  var qc = { isMounted: function(n) {
    return (n = n._reactInternals) ? Ze(n) === n : !1;
  }, enqueueSetState: function(n, r, l) {
    n = n._reactInternals;
    var o = Hn(), c = Li(n), d = qi(o, c);
    d.payload = r, l != null && (d.callback = l), r = Ml(n, d, c), r !== null && (zr(r, n, c, o), Oc(r, n, c));
  }, enqueueReplaceState: function(n, r, l) {
    n = n._reactInternals;
    var o = Hn(), c = Li(n), d = qi(o, c);
    d.tag = 1, d.payload = r, l != null && (d.callback = l), r = Ml(n, d, c), r !== null && (zr(r, n, c, o), Oc(r, n, c));
  }, enqueueForceUpdate: function(n, r) {
    n = n._reactInternals;
    var l = Hn(), o = Li(n), c = qi(l, o);
    c.tag = 2, r != null && (c.callback = r), r = Ml(n, c, o), r !== null && (zr(r, n, o, l), Oc(r, n, o));
  } };
  function jv(n, r, l, o, c, d, m) {
    return n = n.stateNode, typeof n.shouldComponentUpdate == "function" ? n.shouldComponentUpdate(o, d, m) : r.prototype && r.prototype.isPureReactComponent ? !es(l, o) || !es(c, d) : !0;
  }
  function Xc(n, r, l) {
    var o = !1, c = Cr, d = r.contextType;
    return typeof d == "object" && d !== null ? d = Ma(d) : (c = Nn(r) ? Wr : En.current, o = r.contextTypes, d = (o = o != null) ? Gr(n, c) : Cr), r = new r(l, d), n.memoizedState = r.state !== null && r.state !== void 0 ? r.state : null, r.updater = qc, n.stateNode = r, r._reactInternals = n, o && (n = n.stateNode, n.__reactInternalMemoizedUnmaskedChildContext = c, n.__reactInternalMemoizedMaskedChildContext = d), r;
  }
  function Fv(n, r, l, o) {
    n = r.state, typeof r.componentWillReceiveProps == "function" && r.componentWillReceiveProps(l, o), typeof r.UNSAFE_componentWillReceiveProps == "function" && r.UNSAFE_componentWillReceiveProps(l, o), r.state !== n && qc.enqueueReplaceState(r, r.state, null);
  }
  function Rs(n, r, l, o) {
    var c = n.stateNode;
    c.props = l, c.state = n.memoizedState, c.refs = {}, Td(n);
    var d = r.contextType;
    typeof d == "object" && d !== null ? c.context = Ma(d) : (d = Nn(r) ? Wr : En.current, c.context = Gr(n, d)), c.state = n.memoizedState, d = r.getDerivedStateFromProps, typeof d == "function" && (kd(n, r, d, l), c.state = n.memoizedState), typeof r.getDerivedStateFromProps == "function" || typeof c.getSnapshotBeforeUpdate == "function" || typeof c.UNSAFE_componentWillMount != "function" && typeof c.componentWillMount != "function" || (r = c.state, typeof c.componentWillMount == "function" && c.componentWillMount(), typeof c.UNSAFE_componentWillMount == "function" && c.UNSAFE_componentWillMount(), r !== c.state && qc.enqueueReplaceState(c, c.state, null), cs(n, l, c, o), c.state = n.memoizedState), typeof c.componentDidMount == "function" && (n.flags |= 4194308);
  }
  function _u(n, r) {
    try {
      var l = "", o = r;
      do
        l += ft(o), o = o.return;
      while (o);
      var c = l;
    } catch (d) {
      c = `
Error generating stack: ` + d.message + `
` + d.stack;
    }
    return { value: n, source: r, stack: c, digest: null };
  }
  function Dd(n, r, l) {
    return { value: n, source: null, stack: l ?? null, digest: r ?? null };
  }
  function Od(n, r) {
    try {
      console.error(r.value);
    } catch (l) {
      setTimeout(function() {
        throw l;
      });
    }
  }
  var Zc = typeof WeakMap == "function" ? WeakMap : Map;
  function Hv(n, r, l) {
    l = qi(-1, l), l.tag = 3, l.payload = { element: null };
    var o = r.value;
    return l.callback = function() {
      wo || (wo = !0, Ou = o), Od(n, r);
    }, l;
  }
  function Ld(n, r, l) {
    l = qi(-1, l), l.tag = 3;
    var o = n.type.getDerivedStateFromError;
    if (typeof o == "function") {
      var c = r.value;
      l.payload = function() {
        return o(c);
      }, l.callback = function() {
        Od(n, r);
      };
    }
    var d = n.stateNode;
    return d !== null && typeof d.componentDidCatch == "function" && (l.callback = function() {
      Od(n, r), typeof o != "function" && (jl === null ? jl = /* @__PURE__ */ new Set([this]) : jl.add(this));
      var m = r.stack;
      this.componentDidCatch(r.value, { componentStack: m !== null ? m : "" });
    }), l;
  }
  function Md(n, r, l) {
    var o = n.pingCache;
    if (o === null) {
      o = n.pingCache = new Zc();
      var c = /* @__PURE__ */ new Set();
      o.set(r, c);
    } else c = o.get(r), c === void 0 && (c = /* @__PURE__ */ new Set(), o.set(r, c));
    c.has(l) || (c.add(l), n = dy.bind(null, n, r, l), r.then(n, n));
  }
  function Pv(n) {
    do {
      var r;
      if ((r = n.tag === 13) && (r = n.memoizedState, r = r !== null ? r.dehydrated !== null : !0), r) return n;
      n = n.return;
    } while (n !== null);
    return null;
  }
  function Ul(n, r, l, o, c) {
    return n.mode & 1 ? (n.flags |= 65536, n.lanes = c, n) : (n === r ? n.flags |= 65536 : (n.flags |= 128, l.flags |= 131072, l.flags &= -52805, l.tag === 1 && (l.alternate === null ? l.tag = 17 : (r = qi(-1, 1), r.tag = 2, Ml(l, r, 1))), l.lanes |= 1), n);
  }
  var Ts = it.ReactCurrentOwner, An = !1;
  function ur(n, r, l, o) {
    r.child = n === null ? le(r, null, l, o) : wn(r, n.child, l, o);
  }
  function Jr(n, r, l, o, c) {
    l = l.render;
    var d = r.ref;
    return yn(r, c), o = Nl(n, r, l, o, d, c), l = ri(), n !== null && !An ? (r.updateQueue = n.updateQueue, r.flags &= -2053, n.lanes &= ~c, za(n, r, c)) : (dn && l && bc(r), r.flags |= 1, ur(n, r, o, c), r.child);
  }
  function ku(n, r, l, o, c) {
    if (n === null) {
      var d = l.type;
      return typeof d == "function" && !Qd(d) && d.defaultProps === void 0 && l.compare === null && l.defaultProps === void 0 ? (r.tag = 15, r.type = d, et(n, r, d, o, c)) : (n = Hs(l.type, null, o, r, r.mode, c), n.ref = r.ref, n.return = r, r.child = n);
    }
    if (d = n.child, !(n.lanes & c)) {
      var m = d.memoizedProps;
      if (l = l.compare, l = l !== null ? l : es, l(m, o) && n.ref === r.ref) return za(n, r, c);
    }
    return r.flags |= 1, n = Hl(d, o), n.ref = r.ref, n.return = r, r.child = n;
  }
  function et(n, r, l, o, c) {
    if (n !== null) {
      var d = n.memoizedProps;
      if (es(d, o) && n.ref === r.ref) if (An = !1, r.pendingProps = o = d, (n.lanes & c) !== 0) n.flags & 131072 && (An = !0);
      else return r.lanes = n.lanes, za(n, r, c);
    }
    return Vv(n, r, l, o, c);
  }
  function ws(n, r, l) {
    var o = r.pendingProps, c = o.children, d = n !== null ? n.memoizedState : null;
    if (o.mode === "hidden") if (!(r.mode & 1)) r.memoizedState = { baseLanes: 0, cachePool: null, transitions: null }, _e(Co, ma), ma |= l;
    else {
      if (!(l & 1073741824)) return n = d !== null ? d.baseLanes | l : l, r.lanes = r.childLanes = 1073741824, r.memoizedState = { baseLanes: n, cachePool: null, transitions: null }, r.updateQueue = null, _e(Co, ma), ma |= n, null;
      r.memoizedState = { baseLanes: 0, cachePool: null, transitions: null }, o = d !== null ? d.baseLanes : l, _e(Co, ma), ma |= o;
    }
    else d !== null ? (o = d.baseLanes | l, r.memoizedState = null) : o = l, _e(Co, ma), ma |= o;
    return ur(n, r, c, l), r.child;
  }
  function Nd(n, r) {
    var l = r.ref;
    (n === null && l !== null || n !== null && n.ref !== l) && (r.flags |= 512, r.flags |= 2097152);
  }
  function Vv(n, r, l, o, c) {
    var d = Nn(l) ? Wr : En.current;
    return d = Gr(r, d), yn(r, c), l = Nl(n, r, l, o, d, c), o = ri(), n !== null && !An ? (r.updateQueue = n.updateQueue, r.flags &= -2053, n.lanes &= ~c, za(n, r, c)) : (dn && o && bc(r), r.flags |= 1, ur(n, r, l, c), r.child);
  }
  function Bv(n, r, l, o, c) {
    if (Nn(l)) {
      var d = !0;
      Xn(r);
    } else d = !1;
    if (yn(r, c), r.stateNode === null) Na(n, r), Xc(r, l, o), Rs(r, l, o, c), o = !0;
    else if (n === null) {
      var m = r.stateNode, E = r.memoizedProps;
      m.props = E;
      var T = m.context, U = l.contextType;
      typeof U == "object" && U !== null ? U = Ma(U) : (U = Nn(l) ? Wr : En.current, U = Gr(r, U));
      var W = l.getDerivedStateFromProps, K = typeof W == "function" || typeof m.getSnapshotBeforeUpdate == "function";
      K || typeof m.UNSAFE_componentWillReceiveProps != "function" && typeof m.componentWillReceiveProps != "function" || (E !== o || T !== U) && Fv(r, m, o, U), ha = !1;
      var Q = r.memoizedState;
      m.state = Q, cs(r, o, m, c), T = r.memoizedState, E !== o || Q !== T || $n.current || ha ? (typeof W == "function" && (kd(r, l, W, o), T = r.memoizedState), (E = ha || jv(r, l, E, o, Q, T, U)) ? (K || typeof m.UNSAFE_componentWillMount != "function" && typeof m.componentWillMount != "function" || (typeof m.componentWillMount == "function" && m.componentWillMount(), typeof m.UNSAFE_componentWillMount == "function" && m.UNSAFE_componentWillMount()), typeof m.componentDidMount == "function" && (r.flags |= 4194308)) : (typeof m.componentDidMount == "function" && (r.flags |= 4194308), r.memoizedProps = o, r.memoizedState = T), m.props = o, m.state = T, m.context = U, o = E) : (typeof m.componentDidMount == "function" && (r.flags |= 4194308), o = !1);
    } else {
      m = r.stateNode, Nv(n, r), E = r.memoizedProps, U = r.type === r.elementType ? E : ai(r.type, E), m.props = U, K = r.pendingProps, Q = m.context, T = l.contextType, typeof T == "object" && T !== null ? T = Ma(T) : (T = Nn(l) ? Wr : En.current, T = Gr(r, T));
      var fe = l.getDerivedStateFromProps;
      (W = typeof fe == "function" || typeof m.getSnapshotBeforeUpdate == "function") || typeof m.UNSAFE_componentWillReceiveProps != "function" && typeof m.componentWillReceiveProps != "function" || (E !== K || Q !== T) && Fv(r, m, o, T), ha = !1, Q = r.memoizedState, m.state = Q, cs(r, o, m, c);
      var me = r.memoizedState;
      E !== K || Q !== me || $n.current || ha ? (typeof fe == "function" && (kd(r, l, fe, o), me = r.memoizedState), (U = ha || jv(r, l, U, o, Q, me, T) || !1) ? (W || typeof m.UNSAFE_componentWillUpdate != "function" && typeof m.componentWillUpdate != "function" || (typeof m.componentWillUpdate == "function" && m.componentWillUpdate(o, me, T), typeof m.UNSAFE_componentWillUpdate == "function" && m.UNSAFE_componentWillUpdate(o, me, T)), typeof m.componentDidUpdate == "function" && (r.flags |= 4), typeof m.getSnapshotBeforeUpdate == "function" && (r.flags |= 1024)) : (typeof m.componentDidUpdate != "function" || E === n.memoizedProps && Q === n.memoizedState || (r.flags |= 4), typeof m.getSnapshotBeforeUpdate != "function" || E === n.memoizedProps && Q === n.memoizedState || (r.flags |= 1024), r.memoizedProps = o, r.memoizedState = me), m.props = o, m.state = me, m.context = T, o = U) : (typeof m.componentDidUpdate != "function" || E === n.memoizedProps && Q === n.memoizedState || (r.flags |= 4), typeof m.getSnapshotBeforeUpdate != "function" || E === n.memoizedProps && Q === n.memoizedState || (r.flags |= 1024), o = !1);
    }
    return xs(n, r, l, o, d, c);
  }
  function xs(n, r, l, o, c, d) {
    Nd(n, r);
    var m = (r.flags & 128) !== 0;
    if (!o && !m) return c && wc(r, l, !1), za(n, r, d);
    o = r.stateNode, Ts.current = r;
    var E = m && typeof l.getDerivedStateFromError != "function" ? null : o.render();
    return r.flags |= 1, n !== null && m ? (r.child = wn(r, n.child, null, d), r.child = wn(r, null, E, d)) : ur(n, r, E, d), r.memoizedState = o.state, c && wc(r, l, !0), r.child;
  }
  function So(n) {
    var r = n.stateNode;
    r.pendingContext ? Dv(n, r.pendingContext, r.pendingContext !== r.context) : r.context && Dv(n, r.context, !1), xd(n, r.containerInfo);
  }
  function Iv(n, r, l, o, c) {
    return Ll(), Ki(c), r.flags |= 256, ur(n, r, l, o), r.child;
  }
  var Jc = { dehydrated: null, treeContext: null, retryLane: 0 };
  function zd(n) {
    return { baseLanes: n, cachePool: null, transitions: null };
  }
  function ef(n, r, l) {
    var o = r.pendingProps, c = gn.current, d = !1, m = (r.flags & 128) !== 0, E;
    if ((E = m) || (E = n !== null && n.memoizedState === null ? !1 : (c & 2) !== 0), E ? (d = !0, r.flags &= -129) : (n === null || n.memoizedState !== null) && (c |= 1), _e(gn, c & 1), n === null)
      return md(r), n = r.memoizedState, n !== null && (n = n.dehydrated, n !== null) ? (r.mode & 1 ? n.data === "$!" ? r.lanes = 8 : r.lanes = 1073741824 : r.lanes = 1, null) : (m = o.children, n = o.fallback, d ? (o = r.mode, d = r.child, m = { mode: "hidden", children: m }, !(o & 1) && d !== null ? (d.childLanes = 0, d.pendingProps = m) : d = Pl(m, o, 0, null), n = tl(n, o, l, null), d.return = r, n.return = r, d.sibling = n, r.child = d, r.child.memoizedState = zd(l), r.memoizedState = Jc, n) : Ud(r, m));
    if (c = n.memoizedState, c !== null && (E = c.dehydrated, E !== null)) return Yv(n, r, m, o, E, c, l);
    if (d) {
      d = o.fallback, m = r.mode, c = n.child, E = c.sibling;
      var T = { mode: "hidden", children: o.children };
      return !(m & 1) && r.child !== c ? (o = r.child, o.childLanes = 0, o.pendingProps = T, r.deletions = null) : (o = Hl(c, T), o.subtreeFlags = c.subtreeFlags & 14680064), E !== null ? d = Hl(E, d) : (d = tl(d, m, l, null), d.flags |= 2), d.return = r, o.return = r, o.sibling = d, r.child = o, o = d, d = r.child, m = n.child.memoizedState, m = m === null ? zd(l) : { baseLanes: m.baseLanes | l, cachePool: null, transitions: m.transitions }, d.memoizedState = m, d.childLanes = n.childLanes & ~l, r.memoizedState = Jc, o;
    }
    return d = n.child, n = d.sibling, o = Hl(d, { mode: "visible", children: o.children }), !(r.mode & 1) && (o.lanes = l), o.return = r, o.sibling = null, n !== null && (l = r.deletions, l === null ? (r.deletions = [n], r.flags |= 16) : l.push(n)), r.child = o, r.memoizedState = null, o;
  }
  function Ud(n, r) {
    return r = Pl({ mode: "visible", children: r }, n.mode, 0, null), r.return = n, n.child = r;
  }
  function bs(n, r, l, o) {
    return o !== null && Ki(o), wn(r, n.child, null, l), n = Ud(r, r.pendingProps.children), n.flags |= 2, r.memoizedState = null, n;
  }
  function Yv(n, r, l, o, c, d, m) {
    if (l)
      return r.flags & 256 ? (r.flags &= -257, o = Dd(Error(k(422))), bs(n, r, m, o)) : r.memoizedState !== null ? (r.child = n.child, r.flags |= 128, null) : (d = o.fallback, c = r.mode, o = Pl({ mode: "visible", children: o.children }, c, 0, null), d = tl(d, c, m, null), d.flags |= 2, o.return = r, d.return = r, o.sibling = d, r.child = o, r.mode & 1 && wn(r, n.child, null, m), r.child.memoizedState = zd(m), r.memoizedState = Jc, d);
    if (!(r.mode & 1)) return bs(n, r, m, null);
    if (c.data === "$!") {
      if (o = c.nextSibling && c.nextSibling.dataset, o) var E = o.dgst;
      return o = E, d = Error(k(419)), o = Dd(d, o, void 0), bs(n, r, m, o);
    }
    if (E = (m & n.childLanes) !== 0, An || E) {
      if (o = Wn, o !== null) {
        switch (m & -m) {
          case 4:
            c = 2;
            break;
          case 16:
            c = 8;
            break;
          case 64:
          case 128:
          case 256:
          case 512:
          case 1024:
          case 2048:
          case 4096:
          case 8192:
          case 16384:
          case 32768:
          case 65536:
          case 131072:
          case 262144:
          case 524288:
          case 1048576:
          case 2097152:
          case 4194304:
          case 8388608:
          case 16777216:
          case 33554432:
          case 67108864:
            c = 32;
            break;
          case 536870912:
            c = 268435456;
            break;
          default:
            c = 0;
        }
        c = c & (o.suspendedLanes | m) ? 0 : c, c !== 0 && c !== d.retryLane && (d.retryLane = c, va(n, c), zr(o, n, c, -1));
      }
      return $d(), o = Dd(Error(k(421))), bs(n, r, m, o);
    }
    return c.data === "$?" ? (r.flags |= 128, r.child = n.child, r = py.bind(null, n), c._reactRetry = r, null) : (n = d.treeContext, qr = Ei(c.nextSibling), Kr = r, dn = !0, La = null, n !== null && (zn[Oa++] = wi, zn[Oa++] = xi, zn[Oa++] = da, wi = n.id, xi = n.overflow, da = r), r = Ud(r, o.children), r.flags |= 4096, r);
  }
  function Ad(n, r, l) {
    n.lanes |= r;
    var o = n.alternate;
    o !== null && (o.lanes |= r), Ed(n.return, r, l);
  }
  function Lr(n, r, l, o, c) {
    var d = n.memoizedState;
    d === null ? n.memoizedState = { isBackwards: r, rendering: null, renderingStartTime: 0, last: o, tail: l, tailMode: c } : (d.isBackwards = r, d.rendering = null, d.renderingStartTime = 0, d.last = o, d.tail = l, d.tailMode = c);
  }
  function _i(n, r, l) {
    var o = r.pendingProps, c = o.revealOrder, d = o.tail;
    if (ur(n, r, o.children, l), o = gn.current, o & 2) o = o & 1 | 2, r.flags |= 128;
    else {
      if (n !== null && n.flags & 128) e: for (n = r.child; n !== null; ) {
        if (n.tag === 13) n.memoizedState !== null && Ad(n, l, r);
        else if (n.tag === 19) Ad(n, l, r);
        else if (n.child !== null) {
          n.child.return = n, n = n.child;
          continue;
        }
        if (n === r) break e;
        for (; n.sibling === null; ) {
          if (n.return === null || n.return === r) break e;
          n = n.return;
        }
        n.sibling.return = n.return, n = n.sibling;
      }
      o &= 1;
    }
    if (_e(gn, o), !(r.mode & 1)) r.memoizedState = null;
    else switch (c) {
      case "forwards":
        for (l = r.child, c = null; l !== null; ) n = l.alternate, n !== null && Mc(n) === null && (c = l), l = l.sibling;
        l = c, l === null ? (c = r.child, r.child = null) : (c = l.sibling, l.sibling = null), Lr(r, !1, c, l, d);
        break;
      case "backwards":
        for (l = null, c = r.child, r.child = null; c !== null; ) {
          if (n = c.alternate, n !== null && Mc(n) === null) {
            r.child = c;
            break;
          }
          n = c.sibling, c.sibling = l, l = c, c = n;
        }
        Lr(r, !0, l, null, d);
        break;
      case "together":
        Lr(r, !1, null, null, void 0);
        break;
      default:
        r.memoizedState = null;
    }
    return r.child;
  }
  function Na(n, r) {
    !(r.mode & 1) && n !== null && (n.alternate = null, r.alternate = null, r.flags |= 2);
  }
  function za(n, r, l) {
    if (n !== null && (r.dependencies = n.dependencies), Oi |= r.lanes, !(l & r.childLanes)) return null;
    if (n !== null && r.child !== n.child) throw Error(k(153));
    if (r.child !== null) {
      for (n = r.child, l = Hl(n, n.pendingProps), r.child = l, l.return = r; n.sibling !== null; ) n = n.sibling, l = l.sibling = Hl(n, n.pendingProps), l.return = r;
      l.sibling = null;
    }
    return r.child;
  }
  function _s(n, r, l) {
    switch (r.tag) {
      case 3:
        So(r), Ll();
        break;
      case 5:
        Uv(r);
        break;
      case 1:
        Nn(r.type) && Xn(r);
        break;
      case 4:
        xd(r, r.stateNode.containerInfo);
        break;
      case 10:
        var o = r.type._context, c = r.memoizedProps.value;
        _e(pa, o._currentValue), o._currentValue = c;
        break;
      case 13:
        if (o = r.memoizedState, o !== null)
          return o.dehydrated !== null ? (_e(gn, gn.current & 1), r.flags |= 128, null) : l & r.child.childLanes ? ef(n, r, l) : (_e(gn, gn.current & 1), n = za(n, r, l), n !== null ? n.sibling : null);
        _e(gn, gn.current & 1);
        break;
      case 19:
        if (o = (l & r.childLanes) !== 0, n.flags & 128) {
          if (o) return _i(n, r, l);
          r.flags |= 128;
        }
        if (c = r.memoizedState, c !== null && (c.rendering = null, c.tail = null, c.lastEffect = null), _e(gn, gn.current), o) break;
        return null;
      case 22:
      case 23:
        return r.lanes = 0, ws(n, r, l);
    }
    return za(n, r, l);
  }
  var Ua, jn, $v, Qv;
  Ua = function(n, r) {
    for (var l = r.child; l !== null; ) {
      if (l.tag === 5 || l.tag === 6) n.appendChild(l.stateNode);
      else if (l.tag !== 4 && l.child !== null) {
        l.child.return = l, l = l.child;
        continue;
      }
      if (l === r) break;
      for (; l.sibling === null; ) {
        if (l.return === null || l.return === r) return;
        l = l.return;
      }
      l.sibling.return = l.return, l = l.sibling;
    }
  }, jn = function() {
  }, $v = function(n, r, l, o) {
    var c = n.memoizedProps;
    if (c !== o) {
      n = r.stateNode, Su(bi.current);
      var d = null;
      switch (l) {
        case "input":
          c = nr(n, c), o = nr(n, o), d = [];
          break;
        case "select":
          c = ne({}, c, { value: void 0 }), o = ne({}, o, { value: void 0 }), d = [];
          break;
        case "textarea":
          c = In(n, c), o = In(n, o), d = [];
          break;
        default:
          typeof c.onClick != "function" && typeof o.onClick == "function" && (n.onclick = xl);
      }
      on(l, o);
      var m;
      l = null;
      for (U in c) if (!o.hasOwnProperty(U) && c.hasOwnProperty(U) && c[U] != null) if (U === "style") {
        var E = c[U];
        for (m in E) E.hasOwnProperty(m) && (l || (l = {}), l[m] = "");
      } else U !== "dangerouslySetInnerHTML" && U !== "children" && U !== "suppressContentEditableWarning" && U !== "suppressHydrationWarning" && U !== "autoFocus" && (Fe.hasOwnProperty(U) ? d || (d = []) : (d = d || []).push(U, null));
      for (U in o) {
        var T = o[U];
        if (E = c != null ? c[U] : void 0, o.hasOwnProperty(U) && T !== E && (T != null || E != null)) if (U === "style") if (E) {
          for (m in E) !E.hasOwnProperty(m) || T && T.hasOwnProperty(m) || (l || (l = {}), l[m] = "");
          for (m in T) T.hasOwnProperty(m) && E[m] !== T[m] && (l || (l = {}), l[m] = T[m]);
        } else l || (d || (d = []), d.push(
          U,
          l
        )), l = T;
        else U === "dangerouslySetInnerHTML" ? (T = T ? T.__html : void 0, E = E ? E.__html : void 0, T != null && E !== T && (d = d || []).push(U, T)) : U === "children" ? typeof T != "string" && typeof T != "number" || (d = d || []).push(U, "" + T) : U !== "suppressContentEditableWarning" && U !== "suppressHydrationWarning" && (Fe.hasOwnProperty(U) ? (T != null && U === "onScroll" && Vt("scroll", n), d || E === T || (d = [])) : (d = d || []).push(U, T));
      }
      l && (d = d || []).push("style", l);
      var U = d;
      (r.updateQueue = U) && (r.flags |= 4);
    }
  }, Qv = function(n, r, l, o) {
    l !== o && (r.flags |= 4);
  };
  function ks(n, r) {
    if (!dn) switch (n.tailMode) {
      case "hidden":
        r = n.tail;
        for (var l = null; r !== null; ) r.alternate !== null && (l = r), r = r.sibling;
        l === null ? n.tail = null : l.sibling = null;
        break;
      case "collapsed":
        l = n.tail;
        for (var o = null; l !== null; ) l.alternate !== null && (o = l), l = l.sibling;
        o === null ? r || n.tail === null ? n.tail = null : n.tail.sibling = null : o.sibling = null;
    }
  }
  function Jn(n) {
    var r = n.alternate !== null && n.alternate.child === n.child, l = 0, o = 0;
    if (r) for (var c = n.child; c !== null; ) l |= c.lanes | c.childLanes, o |= c.subtreeFlags & 14680064, o |= c.flags & 14680064, c.return = n, c = c.sibling;
    else for (c = n.child; c !== null; ) l |= c.lanes | c.childLanes, o |= c.subtreeFlags, o |= c.flags, c.return = n, c = c.sibling;
    return n.subtreeFlags |= o, n.childLanes = l, r;
  }
  function Wv(n, r, l) {
    var o = r.pendingProps;
    switch (_c(r), r.tag) {
      case 2:
      case 16:
      case 15:
      case 0:
      case 11:
      case 7:
      case 8:
      case 12:
      case 9:
      case 14:
        return Jn(r), null;
      case 1:
        return Nn(r.type) && vo(), Jn(r), null;
      case 3:
        return o = r.stateNode, Eu(), an($n), an(En), Oe(), o.pendingContext && (o.context = o.pendingContext, o.pendingContext = null), (n === null || n.child === null) && (kc(r) ? r.flags |= 4 : n === null || n.memoizedState.isDehydrated && !(r.flags & 256) || (r.flags |= 1024, La !== null && (Lu(La), La = null))), jn(n, r), Jn(r), null;
      case 5:
        Lc(r);
        var c = Su(ps.current);
        if (l = r.type, n !== null && r.stateNode != null) $v(n, r, l, o, c), n.ref !== r.ref && (r.flags |= 512, r.flags |= 2097152);
        else {
          if (!o) {
            if (r.stateNode === null) throw Error(k(166));
            return Jn(r), null;
          }
          if (n = Su(bi.current), kc(r)) {
            o = r.stateNode, l = r.type;
            var d = r.memoizedProps;
            switch (o[Ci] = r, o[ls] = d, n = (r.mode & 1) !== 0, l) {
              case "dialog":
                Vt("cancel", o), Vt("close", o);
                break;
              case "iframe":
              case "object":
              case "embed":
                Vt("load", o);
                break;
              case "video":
              case "audio":
                for (c = 0; c < rs.length; c++) Vt(rs[c], o);
                break;
              case "source":
                Vt("error", o);
                break;
              case "img":
              case "image":
              case "link":
                Vt(
                  "error",
                  o
                ), Vt("load", o);
                break;
              case "details":
                Vt("toggle", o);
                break;
              case "input":
                Vn(o, d), Vt("invalid", o);
                break;
              case "select":
                o._wrapperState = { wasMultiple: !!d.multiple }, Vt("invalid", o);
                break;
              case "textarea":
                gr(o, d), Vt("invalid", o);
            }
            on(l, d), c = null;
            for (var m in d) if (d.hasOwnProperty(m)) {
              var E = d[m];
              m === "children" ? typeof E == "string" ? o.textContent !== E && (d.suppressHydrationWarning !== !0 && Ec(o.textContent, E, n), c = ["children", E]) : typeof E == "number" && o.textContent !== "" + E && (d.suppressHydrationWarning !== !0 && Ec(
                o.textContent,
                E,
                n
              ), c = ["children", "" + E]) : Fe.hasOwnProperty(m) && E != null && m === "onScroll" && Vt("scroll", o);
            }
            switch (l) {
              case "input":
                On(o), ci(o, d, !0);
                break;
              case "textarea":
                On(o), Ln(o);
                break;
              case "select":
              case "option":
                break;
              default:
                typeof d.onClick == "function" && (o.onclick = xl);
            }
            o = c, r.updateQueue = o, o !== null && (r.flags |= 4);
          } else {
            m = c.nodeType === 9 ? c : c.ownerDocument, n === "http://www.w3.org/1999/xhtml" && (n = Sr(l)), n === "http://www.w3.org/1999/xhtml" ? l === "script" ? (n = m.createElement("div"), n.innerHTML = "<script><\/script>", n = n.removeChild(n.firstChild)) : typeof o.is == "string" ? n = m.createElement(l, { is: o.is }) : (n = m.createElement(l), l === "select" && (m = n, o.multiple ? m.multiple = !0 : o.size && (m.size = o.size))) : n = m.createElementNS(n, l), n[Ci] = r, n[ls] = o, Ua(n, r, !1, !1), r.stateNode = n;
            e: {
              switch (m = qn(l, o), l) {
                case "dialog":
                  Vt("cancel", n), Vt("close", n), c = o;
                  break;
                case "iframe":
                case "object":
                case "embed":
                  Vt("load", n), c = o;
                  break;
                case "video":
                case "audio":
                  for (c = 0; c < rs.length; c++) Vt(rs[c], n);
                  c = o;
                  break;
                case "source":
                  Vt("error", n), c = o;
                  break;
                case "img":
                case "image":
                case "link":
                  Vt(
                    "error",
                    n
                  ), Vt("load", n), c = o;
                  break;
                case "details":
                  Vt("toggle", n), c = o;
                  break;
                case "input":
                  Vn(n, o), c = nr(n, o), Vt("invalid", n);
                  break;
                case "option":
                  c = o;
                  break;
                case "select":
                  n._wrapperState = { wasMultiple: !!o.multiple }, c = ne({}, o, { value: void 0 }), Vt("invalid", n);
                  break;
                case "textarea":
                  gr(n, o), c = In(n, o), Vt("invalid", n);
                  break;
                default:
                  c = o;
              }
              on(l, c), E = c;
              for (d in E) if (E.hasOwnProperty(d)) {
                var T = E[d];
                d === "style" ? en(n, T) : d === "dangerouslySetInnerHTML" ? (T = T ? T.__html : void 0, T != null && fi(n, T)) : d === "children" ? typeof T == "string" ? (l !== "textarea" || T !== "") && ee(n, T) : typeof T == "number" && ee(n, "" + T) : d !== "suppressContentEditableWarning" && d !== "suppressHydrationWarning" && d !== "autoFocus" && (Fe.hasOwnProperty(d) ? T != null && d === "onScroll" && Vt("scroll", n) : T != null && Le(n, d, T, m));
              }
              switch (l) {
                case "input":
                  On(n), ci(n, o, !1);
                  break;
                case "textarea":
                  On(n), Ln(n);
                  break;
                case "option":
                  o.value != null && n.setAttribute("value", "" + ut(o.value));
                  break;
                case "select":
                  n.multiple = !!o.multiple, d = o.value, d != null ? Rn(n, !!o.multiple, d, !1) : o.defaultValue != null && Rn(
                    n,
                    !!o.multiple,
                    o.defaultValue,
                    !0
                  );
                  break;
                default:
                  typeof c.onClick == "function" && (n.onclick = xl);
              }
              switch (l) {
                case "button":
                case "input":
                case "select":
                case "textarea":
                  o = !!o.autoFocus;
                  break e;
                case "img":
                  o = !0;
                  break e;
                default:
                  o = !1;
              }
            }
            o && (r.flags |= 4);
          }
          r.ref !== null && (r.flags |= 512, r.flags |= 2097152);
        }
        return Jn(r), null;
      case 6:
        if (n && r.stateNode != null) Qv(n, r, n.memoizedProps, o);
        else {
          if (typeof o != "string" && r.stateNode === null) throw Error(k(166));
          if (l = Su(ps.current), Su(bi.current), kc(r)) {
            if (o = r.stateNode, l = r.memoizedProps, o[Ci] = r, (d = o.nodeValue !== l) && (n = Kr, n !== null)) switch (n.tag) {
              case 3:
                Ec(o.nodeValue, l, (n.mode & 1) !== 0);
                break;
              case 5:
                n.memoizedProps.suppressHydrationWarning !== !0 && Ec(o.nodeValue, l, (n.mode & 1) !== 0);
            }
            d && (r.flags |= 4);
          } else o = (l.nodeType === 9 ? l : l.ownerDocument).createTextNode(o), o[Ci] = r, r.stateNode = o;
        }
        return Jn(r), null;
      case 13:
        if (an(gn), o = r.memoizedState, n === null || n.memoizedState !== null && n.memoizedState.dehydrated !== null) {
          if (dn && qr !== null && r.mode & 1 && !(r.flags & 128)) ss(), Ll(), r.flags |= 98560, d = !1;
          else if (d = kc(r), o !== null && o.dehydrated !== null) {
            if (n === null) {
              if (!d) throw Error(k(318));
              if (d = r.memoizedState, d = d !== null ? d.dehydrated : null, !d) throw Error(k(317));
              d[Ci] = r;
            } else Ll(), !(r.flags & 128) && (r.memoizedState = null), r.flags |= 4;
            Jn(r), d = !1;
          } else La !== null && (Lu(La), La = null), d = !0;
          if (!d) return r.flags & 65536 ? r : null;
        }
        return r.flags & 128 ? (r.lanes = l, r) : (o = o !== null, o !== (n !== null && n.memoizedState !== null) && o && (r.child.flags |= 8192, r.mode & 1 && (n === null || gn.current & 1 ? _n === 0 && (_n = 3) : $d())), r.updateQueue !== null && (r.flags |= 4), Jn(r), null);
      case 4:
        return Eu(), jn(n, r), n === null && oo(r.stateNode.containerInfo), Jn(r), null;
      case 10:
        return Sd(r.type._context), Jn(r), null;
      case 17:
        return Nn(r.type) && vo(), Jn(r), null;
      case 19:
        if (an(gn), d = r.memoizedState, d === null) return Jn(r), null;
        if (o = (r.flags & 128) !== 0, m = d.rendering, m === null) if (o) ks(d, !1);
        else {
          if (_n !== 0 || n !== null && n.flags & 128) for (n = r.child; n !== null; ) {
            if (m = Mc(n), m !== null) {
              for (r.flags |= 128, ks(d, !1), o = m.updateQueue, o !== null && (r.updateQueue = o, r.flags |= 4), r.subtreeFlags = 0, o = l, l = r.child; l !== null; ) d = l, n = o, d.flags &= 14680066, m = d.alternate, m === null ? (d.childLanes = 0, d.lanes = n, d.child = null, d.subtreeFlags = 0, d.memoizedProps = null, d.memoizedState = null, d.updateQueue = null, d.dependencies = null, d.stateNode = null) : (d.childLanes = m.childLanes, d.lanes = m.lanes, d.child = m.child, d.subtreeFlags = 0, d.deletions = null, d.memoizedProps = m.memoizedProps, d.memoizedState = m.memoizedState, d.updateQueue = m.updateQueue, d.type = m.type, n = m.dependencies, d.dependencies = n === null ? null : { lanes: n.lanes, firstContext: n.firstContext }), l = l.sibling;
              return _e(gn, gn.current & 1 | 2), r.child;
            }
            n = n.sibling;
          }
          d.tail !== null && Je() > To && (r.flags |= 128, o = !0, ks(d, !1), r.lanes = 4194304);
        }
        else {
          if (!o) if (n = Mc(m), n !== null) {
            if (r.flags |= 128, o = !0, l = n.updateQueue, l !== null && (r.updateQueue = l, r.flags |= 4), ks(d, !0), d.tail === null && d.tailMode === "hidden" && !m.alternate && !dn) return Jn(r), null;
          } else 2 * Je() - d.renderingStartTime > To && l !== 1073741824 && (r.flags |= 128, o = !0, ks(d, !1), r.lanes = 4194304);
          d.isBackwards ? (m.sibling = r.child, r.child = m) : (l = d.last, l !== null ? l.sibling = m : r.child = m, d.last = m);
        }
        return d.tail !== null ? (r = d.tail, d.rendering = r, d.tail = r.sibling, d.renderingStartTime = Je(), r.sibling = null, l = gn.current, _e(gn, o ? l & 1 | 2 : l & 1), r) : (Jn(r), null);
      case 22:
      case 23:
        return Yd(), o = r.memoizedState !== null, n !== null && n.memoizedState !== null !== o && (r.flags |= 8192), o && r.mode & 1 ? ma & 1073741824 && (Jn(r), r.subtreeFlags & 6 && (r.flags |= 8192)) : Jn(r), null;
      case 24:
        return null;
      case 25:
        return null;
    }
    throw Error(k(156, r.tag));
  }
  function tf(n, r) {
    switch (_c(r), r.tag) {
      case 1:
        return Nn(r.type) && vo(), n = r.flags, n & 65536 ? (r.flags = n & -65537 | 128, r) : null;
      case 3:
        return Eu(), an($n), an(En), Oe(), n = r.flags, n & 65536 && !(n & 128) ? (r.flags = n & -65537 | 128, r) : null;
      case 5:
        return Lc(r), null;
      case 13:
        if (an(gn), n = r.memoizedState, n !== null && n.dehydrated !== null) {
          if (r.alternate === null) throw Error(k(340));
          Ll();
        }
        return n = r.flags, n & 65536 ? (r.flags = n & -65537 | 128, r) : null;
      case 19:
        return an(gn), null;
      case 4:
        return Eu(), null;
      case 10:
        return Sd(r.type._context), null;
      case 22:
      case 23:
        return Yd(), null;
      case 24:
        return null;
      default:
        return null;
    }
  }
  var Ds = !1, Tr = !1, ly = typeof WeakSet == "function" ? WeakSet : Set, ve = null;
  function Eo(n, r) {
    var l = n.ref;
    if (l !== null) if (typeof l == "function") try {
      l(null);
    } catch (o) {
      pn(n, r, o);
    }
    else l.current = null;
  }
  function nf(n, r, l) {
    try {
      l();
    } catch (o) {
      pn(n, r, o);
    }
  }
  var Gv = !1;
  function Kv(n, r) {
    if (is = ba, n = ts(), dc(n)) {
      if ("selectionStart" in n) var l = { start: n.selectionStart, end: n.selectionEnd };
      else e: {
        l = (l = n.ownerDocument) && l.defaultView || window;
        var o = l.getSelection && l.getSelection();
        if (o && o.rangeCount !== 0) {
          l = o.anchorNode;
          var c = o.anchorOffset, d = o.focusNode;
          o = o.focusOffset;
          try {
            l.nodeType, d.nodeType;
          } catch {
            l = null;
            break e;
          }
          var m = 0, E = -1, T = -1, U = 0, W = 0, K = n, Q = null;
          t: for (; ; ) {
            for (var fe; K !== l || c !== 0 && K.nodeType !== 3 || (E = m + c), K !== d || o !== 0 && K.nodeType !== 3 || (T = m + o), K.nodeType === 3 && (m += K.nodeValue.length), (fe = K.firstChild) !== null; )
              Q = K, K = fe;
            for (; ; ) {
              if (K === n) break t;
              if (Q === l && ++U === c && (E = m), Q === d && ++W === o && (T = m), (fe = K.nextSibling) !== null) break;
              K = Q, Q = K.parentNode;
            }
            K = fe;
          }
          l = E === -1 || T === -1 ? null : { start: E, end: T };
        } else l = null;
      }
      l = l || { start: 0, end: 0 };
    } else l = null;
    for (pu = { focusedElem: n, selectionRange: l }, ba = !1, ve = r; ve !== null; ) if (r = ve, n = r.child, (r.subtreeFlags & 1028) !== 0 && n !== null) n.return = r, ve = n;
    else for (; ve !== null; ) {
      r = ve;
      try {
        var me = r.alternate;
        if (r.flags & 1024) switch (r.tag) {
          case 0:
          case 11:
          case 15:
            break;
          case 1:
            if (me !== null) {
              var Ce = me.memoizedProps, kn = me.memoizedState, D = r.stateNode, x = D.getSnapshotBeforeUpdate(r.elementType === r.type ? Ce : ai(r.type, Ce), kn);
              D.__reactInternalSnapshotBeforeUpdate = x;
            }
            break;
          case 3:
            var M = r.stateNode.containerInfo;
            M.nodeType === 1 ? M.textContent = "" : M.nodeType === 9 && M.documentElement && M.removeChild(M.documentElement);
            break;
          case 5:
          case 6:
          case 4:
          case 17:
            break;
          default:
            throw Error(k(163));
        }
      } catch (G) {
        pn(r, r.return, G);
      }
      if (n = r.sibling, n !== null) {
        n.return = r.return, ve = n;
        break;
      }
      ve = r.return;
    }
    return me = Gv, Gv = !1, me;
  }
  function Os(n, r, l) {
    var o = r.updateQueue;
    if (o = o !== null ? o.lastEffect : null, o !== null) {
      var c = o = o.next;
      do {
        if ((c.tag & n) === n) {
          var d = c.destroy;
          c.destroy = void 0, d !== void 0 && nf(r, l, d);
        }
        c = c.next;
      } while (c !== o);
    }
  }
  function Ls(n, r) {
    if (r = r.updateQueue, r = r !== null ? r.lastEffect : null, r !== null) {
      var l = r = r.next;
      do {
        if ((l.tag & n) === n) {
          var o = l.create;
          l.destroy = o();
        }
        l = l.next;
      } while (l !== r);
    }
  }
  function jd(n) {
    var r = n.ref;
    if (r !== null) {
      var l = n.stateNode;
      switch (n.tag) {
        case 5:
          n = l;
          break;
        default:
          n = l;
      }
      typeof r == "function" ? r(n) : r.current = n;
    }
  }
  function rf(n) {
    var r = n.alternate;
    r !== null && (n.alternate = null, rf(r)), n.child = null, n.deletions = null, n.sibling = null, n.tag === 5 && (r = n.stateNode, r !== null && (delete r[Ci], delete r[ls], delete r[us], delete r[po], delete r[ay])), n.stateNode = null, n.return = null, n.dependencies = null, n.memoizedProps = null, n.memoizedState = null, n.pendingProps = null, n.stateNode = null, n.updateQueue = null;
  }
  function Ms(n) {
    return n.tag === 5 || n.tag === 3 || n.tag === 4;
  }
  function Zi(n) {
    e: for (; ; ) {
      for (; n.sibling === null; ) {
        if (n.return === null || Ms(n.return)) return null;
        n = n.return;
      }
      for (n.sibling.return = n.return, n = n.sibling; n.tag !== 5 && n.tag !== 6 && n.tag !== 18; ) {
        if (n.flags & 2 || n.child === null || n.tag === 4) continue e;
        n.child.return = n, n = n.child;
      }
      if (!(n.flags & 2)) return n.stateNode;
    }
  }
  function ki(n, r, l) {
    var o = n.tag;
    if (o === 5 || o === 6) n = n.stateNode, r ? l.nodeType === 8 ? l.parentNode.insertBefore(n, r) : l.insertBefore(n, r) : (l.nodeType === 8 ? (r = l.parentNode, r.insertBefore(n, l)) : (r = l, r.appendChild(n)), l = l._reactRootContainer, l != null || r.onclick !== null || (r.onclick = xl));
    else if (o !== 4 && (n = n.child, n !== null)) for (ki(n, r, l), n = n.sibling; n !== null; ) ki(n, r, l), n = n.sibling;
  }
  function Di(n, r, l) {
    var o = n.tag;
    if (o === 5 || o === 6) n = n.stateNode, r ? l.insertBefore(n, r) : l.appendChild(n);
    else if (o !== 4 && (n = n.child, n !== null)) for (Di(n, r, l), n = n.sibling; n !== null; ) Di(n, r, l), n = n.sibling;
  }
  var bn = null, Mr = !1;
  function Nr(n, r, l) {
    for (l = l.child; l !== null; ) qv(n, r, l), l = l.sibling;
  }
  function qv(n, r, l) {
    if ($r && typeof $r.onCommitFiberUnmount == "function") try {
      $r.onCommitFiberUnmount(ml, l);
    } catch {
    }
    switch (l.tag) {
      case 5:
        Tr || Eo(l, r);
      case 6:
        var o = bn, c = Mr;
        bn = null, Nr(n, r, l), bn = o, Mr = c, bn !== null && (Mr ? (n = bn, l = l.stateNode, n.nodeType === 8 ? n.parentNode.removeChild(l) : n.removeChild(l)) : bn.removeChild(l.stateNode));
        break;
      case 18:
        bn !== null && (Mr ? (n = bn, l = l.stateNode, n.nodeType === 8 ? fo(n.parentNode, l) : n.nodeType === 1 && fo(n, l), Ja(n)) : fo(bn, l.stateNode));
        break;
      case 4:
        o = bn, c = Mr, bn = l.stateNode.containerInfo, Mr = !0, Nr(n, r, l), bn = o, Mr = c;
        break;
      case 0:
      case 11:
      case 14:
      case 15:
        if (!Tr && (o = l.updateQueue, o !== null && (o = o.lastEffect, o !== null))) {
          c = o = o.next;
          do {
            var d = c, m = d.destroy;
            d = d.tag, m !== void 0 && (d & 2 || d & 4) && nf(l, r, m), c = c.next;
          } while (c !== o);
        }
        Nr(n, r, l);
        break;
      case 1:
        if (!Tr && (Eo(l, r), o = l.stateNode, typeof o.componentWillUnmount == "function")) try {
          o.props = l.memoizedProps, o.state = l.memoizedState, o.componentWillUnmount();
        } catch (E) {
          pn(l, r, E);
        }
        Nr(n, r, l);
        break;
      case 21:
        Nr(n, r, l);
        break;
      case 22:
        l.mode & 1 ? (Tr = (o = Tr) || l.memoizedState !== null, Nr(n, r, l), Tr = o) : Nr(n, r, l);
        break;
      default:
        Nr(n, r, l);
    }
  }
  function Xv(n) {
    var r = n.updateQueue;
    if (r !== null) {
      n.updateQueue = null;
      var l = n.stateNode;
      l === null && (l = n.stateNode = new ly()), r.forEach(function(o) {
        var c = lh.bind(null, n, o);
        l.has(o) || (l.add(o), o.then(c, c));
      });
    }
  }
  function ii(n, r) {
    var l = r.deletions;
    if (l !== null) for (var o = 0; o < l.length; o++) {
      var c = l[o];
      try {
        var d = n, m = r, E = m;
        e: for (; E !== null; ) {
          switch (E.tag) {
            case 5:
              bn = E.stateNode, Mr = !1;
              break e;
            case 3:
              bn = E.stateNode.containerInfo, Mr = !0;
              break e;
            case 4:
              bn = E.stateNode.containerInfo, Mr = !0;
              break e;
          }
          E = E.return;
        }
        if (bn === null) throw Error(k(160));
        qv(d, m, c), bn = null, Mr = !1;
        var T = c.alternate;
        T !== null && (T.return = null), c.return = null;
      } catch (U) {
        pn(c, r, U);
      }
    }
    if (r.subtreeFlags & 12854) for (r = r.child; r !== null; ) Fd(r, n), r = r.sibling;
  }
  function Fd(n, r) {
    var l = n.alternate, o = n.flags;
    switch (n.tag) {
      case 0:
      case 11:
      case 14:
      case 15:
        if (ii(r, n), ea(n), o & 4) {
          try {
            Os(3, n, n.return), Ls(3, n);
          } catch (Ce) {
            pn(n, n.return, Ce);
          }
          try {
            Os(5, n, n.return);
          } catch (Ce) {
            pn(n, n.return, Ce);
          }
        }
        break;
      case 1:
        ii(r, n), ea(n), o & 512 && l !== null && Eo(l, l.return);
        break;
      case 5:
        if (ii(r, n), ea(n), o & 512 && l !== null && Eo(l, l.return), n.flags & 32) {
          var c = n.stateNode;
          try {
            ee(c, "");
          } catch (Ce) {
            pn(n, n.return, Ce);
          }
        }
        if (o & 4 && (c = n.stateNode, c != null)) {
          var d = n.memoizedProps, m = l !== null ? l.memoizedProps : d, E = n.type, T = n.updateQueue;
          if (n.updateQueue = null, T !== null) try {
            E === "input" && d.type === "radio" && d.name != null && Bn(c, d), qn(E, m);
            var U = qn(E, d);
            for (m = 0; m < T.length; m += 2) {
              var W = T[m], K = T[m + 1];
              W === "style" ? en(c, K) : W === "dangerouslySetInnerHTML" ? fi(c, K) : W === "children" ? ee(c, K) : Le(c, W, K, U);
            }
            switch (E) {
              case "input":
                Yr(c, d);
                break;
              case "textarea":
                $a(c, d);
                break;
              case "select":
                var Q = c._wrapperState.wasMultiple;
                c._wrapperState.wasMultiple = !!d.multiple;
                var fe = d.value;
                fe != null ? Rn(c, !!d.multiple, fe, !1) : Q !== !!d.multiple && (d.defaultValue != null ? Rn(
                  c,
                  !!d.multiple,
                  d.defaultValue,
                  !0
                ) : Rn(c, !!d.multiple, d.multiple ? [] : "", !1));
            }
            c[ls] = d;
          } catch (Ce) {
            pn(n, n.return, Ce);
          }
        }
        break;
      case 6:
        if (ii(r, n), ea(n), o & 4) {
          if (n.stateNode === null) throw Error(k(162));
          c = n.stateNode, d = n.memoizedProps;
          try {
            c.nodeValue = d;
          } catch (Ce) {
            pn(n, n.return, Ce);
          }
        }
        break;
      case 3:
        if (ii(r, n), ea(n), o & 4 && l !== null && l.memoizedState.isDehydrated) try {
          Ja(r.containerInfo);
        } catch (Ce) {
          pn(n, n.return, Ce);
        }
        break;
      case 4:
        ii(r, n), ea(n);
        break;
      case 13:
        ii(r, n), ea(n), c = n.child, c.flags & 8192 && (d = c.memoizedState !== null, c.stateNode.isHidden = d, !d || c.alternate !== null && c.alternate.memoizedState !== null || (Vd = Je())), o & 4 && Xv(n);
        break;
      case 22:
        if (W = l !== null && l.memoizedState !== null, n.mode & 1 ? (Tr = (U = Tr) || W, ii(r, n), Tr = U) : ii(r, n), ea(n), o & 8192) {
          if (U = n.memoizedState !== null, (n.stateNode.isHidden = U) && !W && n.mode & 1) for (ve = n, W = n.child; W !== null; ) {
            for (K = ve = W; ve !== null; ) {
              switch (Q = ve, fe = Q.child, Q.tag) {
                case 0:
                case 11:
                case 14:
                case 15:
                  Os(4, Q, Q.return);
                  break;
                case 1:
                  Eo(Q, Q.return);
                  var me = Q.stateNode;
                  if (typeof me.componentWillUnmount == "function") {
                    o = Q, l = Q.return;
                    try {
                      r = o, me.props = r.memoizedProps, me.state = r.memoizedState, me.componentWillUnmount();
                    } catch (Ce) {
                      pn(o, l, Ce);
                    }
                  }
                  break;
                case 5:
                  Eo(Q, Q.return);
                  break;
                case 22:
                  if (Q.memoizedState !== null) {
                    Ns(K);
                    continue;
                  }
              }
              fe !== null ? (fe.return = Q, ve = fe) : Ns(K);
            }
            W = W.sibling;
          }
          e: for (W = null, K = n; ; ) {
            if (K.tag === 5) {
              if (W === null) {
                W = K;
                try {
                  c = K.stateNode, U ? (d = c.style, typeof d.setProperty == "function" ? d.setProperty("display", "none", "important") : d.display = "none") : (E = K.stateNode, T = K.memoizedProps.style, m = T != null && T.hasOwnProperty("display") ? T.display : null, E.style.display = Ht("display", m));
                } catch (Ce) {
                  pn(n, n.return, Ce);
                }
              }
            } else if (K.tag === 6) {
              if (W === null) try {
                K.stateNode.nodeValue = U ? "" : K.memoizedProps;
              } catch (Ce) {
                pn(n, n.return, Ce);
              }
            } else if ((K.tag !== 22 && K.tag !== 23 || K.memoizedState === null || K === n) && K.child !== null) {
              K.child.return = K, K = K.child;
              continue;
            }
            if (K === n) break e;
            for (; K.sibling === null; ) {
              if (K.return === null || K.return === n) break e;
              W === K && (W = null), K = K.return;
            }
            W === K && (W = null), K.sibling.return = K.return, K = K.sibling;
          }
        }
        break;
      case 19:
        ii(r, n), ea(n), o & 4 && Xv(n);
        break;
      case 21:
        break;
      default:
        ii(
          r,
          n
        ), ea(n);
    }
  }
  function ea(n) {
    var r = n.flags;
    if (r & 2) {
      try {
        e: {
          for (var l = n.return; l !== null; ) {
            if (Ms(l)) {
              var o = l;
              break e;
            }
            l = l.return;
          }
          throw Error(k(160));
        }
        switch (o.tag) {
          case 5:
            var c = o.stateNode;
            o.flags & 32 && (ee(c, ""), o.flags &= -33);
            var d = Zi(n);
            Di(n, d, c);
            break;
          case 3:
          case 4:
            var m = o.stateNode.containerInfo, E = Zi(n);
            ki(n, E, m);
            break;
          default:
            throw Error(k(161));
        }
      } catch (T) {
        pn(n, n.return, T);
      }
      n.flags &= -3;
    }
    r & 4096 && (n.flags &= -4097);
  }
  function uy(n, r, l) {
    ve = n, Hd(n);
  }
  function Hd(n, r, l) {
    for (var o = (n.mode & 1) !== 0; ve !== null; ) {
      var c = ve, d = c.child;
      if (c.tag === 22 && o) {
        var m = c.memoizedState !== null || Ds;
        if (!m) {
          var E = c.alternate, T = E !== null && E.memoizedState !== null || Tr;
          E = Ds;
          var U = Tr;
          if (Ds = m, (Tr = T) && !U) for (ve = c; ve !== null; ) m = ve, T = m.child, m.tag === 22 && m.memoizedState !== null ? Pd(c) : T !== null ? (T.return = m, ve = T) : Pd(c);
          for (; d !== null; ) ve = d, Hd(d), d = d.sibling;
          ve = c, Ds = E, Tr = U;
        }
        Zv(n);
      } else c.subtreeFlags & 8772 && d !== null ? (d.return = c, ve = d) : Zv(n);
    }
  }
  function Zv(n) {
    for (; ve !== null; ) {
      var r = ve;
      if (r.flags & 8772) {
        var l = r.alternate;
        try {
          if (r.flags & 8772) switch (r.tag) {
            case 0:
            case 11:
            case 15:
              Tr || Ls(5, r);
              break;
            case 1:
              var o = r.stateNode;
              if (r.flags & 4 && !Tr) if (l === null) o.componentDidMount();
              else {
                var c = r.elementType === r.type ? l.memoizedProps : ai(r.type, l.memoizedProps);
                o.componentDidUpdate(c, l.memoizedState, o.__reactInternalSnapshotBeforeUpdate);
              }
              var d = r.updateQueue;
              d !== null && wd(r, d, o);
              break;
            case 3:
              var m = r.updateQueue;
              if (m !== null) {
                if (l = null, r.child !== null) switch (r.child.tag) {
                  case 5:
                    l = r.child.stateNode;
                    break;
                  case 1:
                    l = r.child.stateNode;
                }
                wd(r, m, l);
              }
              break;
            case 5:
              var E = r.stateNode;
              if (l === null && r.flags & 4) {
                l = E;
                var T = r.memoizedProps;
                switch (r.type) {
                  case "button":
                  case "input":
                  case "select":
                  case "textarea":
                    T.autoFocus && l.focus();
                    break;
                  case "img":
                    T.src && (l.src = T.src);
                }
              }
              break;
            case 6:
              break;
            case 4:
              break;
            case 12:
              break;
            case 13:
              if (r.memoizedState === null) {
                var U = r.alternate;
                if (U !== null) {
                  var W = U.memoizedState;
                  if (W !== null) {
                    var K = W.dehydrated;
                    K !== null && Ja(K);
                  }
                }
              }
              break;
            case 19:
            case 17:
            case 21:
            case 22:
            case 23:
            case 25:
              break;
            default:
              throw Error(k(163));
          }
          Tr || r.flags & 512 && jd(r);
        } catch (Q) {
          pn(r, r.return, Q);
        }
      }
      if (r === n) {
        ve = null;
        break;
      }
      if (l = r.sibling, l !== null) {
        l.return = r.return, ve = l;
        break;
      }
      ve = r.return;
    }
  }
  function Ns(n) {
    for (; ve !== null; ) {
      var r = ve;
      if (r === n) {
        ve = null;
        break;
      }
      var l = r.sibling;
      if (l !== null) {
        l.return = r.return, ve = l;
        break;
      }
      ve = r.return;
    }
  }
  function Pd(n) {
    for (; ve !== null; ) {
      var r = ve;
      try {
        switch (r.tag) {
          case 0:
          case 11:
          case 15:
            var l = r.return;
            try {
              Ls(4, r);
            } catch (T) {
              pn(r, l, T);
            }
            break;
          case 1:
            var o = r.stateNode;
            if (typeof o.componentDidMount == "function") {
              var c = r.return;
              try {
                o.componentDidMount();
              } catch (T) {
                pn(r, c, T);
              }
            }
            var d = r.return;
            try {
              jd(r);
            } catch (T) {
              pn(r, d, T);
            }
            break;
          case 5:
            var m = r.return;
            try {
              jd(r);
            } catch (T) {
              pn(r, m, T);
            }
        }
      } catch (T) {
        pn(r, r.return, T);
      }
      if (r === n) {
        ve = null;
        break;
      }
      var E = r.sibling;
      if (E !== null) {
        E.return = r.return, ve = E;
        break;
      }
      ve = r.return;
    }
  }
  var oy = Math.ceil, Al = it.ReactCurrentDispatcher, Du = it.ReactCurrentOwner, or = it.ReactCurrentBatchConfig, Rt = 0, Wn = null, Fn = null, sr = 0, ma = 0, Co = Da(0), _n = 0, zs = null, Oi = 0, Ro = 0, af = 0, Us = null, ta = null, Vd = 0, To = 1 / 0, ya = null, wo = !1, Ou = null, jl = null, lf = !1, Ji = null, As = 0, Fl = 0, xo = null, js = -1, wr = 0;
  function Hn() {
    return Rt & 6 ? Je() : js !== -1 ? js : js = Je();
  }
  function Li(n) {
    return n.mode & 1 ? Rt & 2 && sr !== 0 ? sr & -sr : iy.transition !== null ? (wr === 0 && (wr = qu()), wr) : (n = Lt, n !== 0 || (n = window.event, n = n === void 0 ? 16 : ro(n.type)), n) : 1;
  }
  function zr(n, r, l, o) {
    if (50 < Fl) throw Fl = 0, xo = null, Error(k(185));
    Pi(n, l, o), (!(Rt & 2) || n !== Wn) && (n === Wn && (!(Rt & 2) && (Ro |= l), _n === 4 && li(n, sr)), na(n, o), l === 1 && Rt === 0 && !(r.mode & 1) && (To = Je() + 500, ho && Ti()));
  }
  function na(n, r) {
    var l = n.callbackNode;
    au(n, r);
    var o = Za(n, n === Wn ? sr : 0);
    if (o === 0) l !== null && ar(l), n.callbackNode = null, n.callbackPriority = 0;
    else if (r = o & -o, n.callbackPriority !== r) {
      if (l != null && ar(l), r === 1) n.tag === 0 ? _l(Bd.bind(null, n)) : xc(Bd.bind(null, n)), co(function() {
        !(Rt & 6) && Ti();
      }), l = null;
      else {
        switch (Zu(o)) {
          case 1:
            l = qa;
            break;
          case 4:
            l = nu;
            break;
          case 16:
            l = ru;
            break;
          case 536870912:
            l = Wu;
            break;
          default:
            l = ru;
        }
        l = oh(l, uf.bind(null, n));
      }
      n.callbackPriority = r, n.callbackNode = l;
    }
  }
  function uf(n, r) {
    if (js = -1, wr = 0, Rt & 6) throw Error(k(327));
    var l = n.callbackNode;
    if (bo() && n.callbackNode !== l) return null;
    var o = Za(n, n === Wn ? sr : 0);
    if (o === 0) return null;
    if (o & 30 || o & n.expiredLanes || r) r = of(n, o);
    else {
      r = o;
      var c = Rt;
      Rt |= 2;
      var d = eh();
      (Wn !== n || sr !== r) && (ya = null, To = Je() + 500, el(n, r));
      do
        try {
          th();
          break;
        } catch (E) {
          Jv(n, E);
        }
      while (!0);
      gd(), Al.current = d, Rt = c, Fn !== null ? r = 0 : (Wn = null, sr = 0, r = _n);
    }
    if (r !== 0) {
      if (r === 2 && (c = gl(n), c !== 0 && (o = c, r = Fs(n, c))), r === 1) throw l = zs, el(n, 0), li(n, o), na(n, Je()), l;
      if (r === 6) li(n, o);
      else {
        if (c = n.current.alternate, !(o & 30) && !sy(c) && (r = of(n, o), r === 2 && (d = gl(n), d !== 0 && (o = d, r = Fs(n, d))), r === 1)) throw l = zs, el(n, 0), li(n, o), na(n, Je()), l;
        switch (n.finishedWork = c, n.finishedLanes = o, r) {
          case 0:
          case 1:
            throw Error(k(345));
          case 2:
            Nu(n, ta, ya);
            break;
          case 3:
            if (li(n, o), (o & 130023424) === o && (r = Vd + 500 - Je(), 10 < r)) {
              if (Za(n, 0) !== 0) break;
              if (c = n.suspendedLanes, (c & o) !== o) {
                Hn(), n.pingedLanes |= n.suspendedLanes & c;
                break;
              }
              n.timeoutHandle = Rc(Nu.bind(null, n, ta, ya), r);
              break;
            }
            Nu(n, ta, ya);
            break;
          case 4:
            if (li(n, o), (o & 4194240) === o) break;
            for (r = n.eventTimes, c = -1; 0 < o; ) {
              var m = 31 - kr(o);
              d = 1 << m, m = r[m], m > c && (c = m), o &= ~d;
            }
            if (o = c, o = Je() - o, o = (120 > o ? 120 : 480 > o ? 480 : 1080 > o ? 1080 : 1920 > o ? 1920 : 3e3 > o ? 3e3 : 4320 > o ? 4320 : 1960 * oy(o / 1960)) - o, 10 < o) {
              n.timeoutHandle = Rc(Nu.bind(null, n, ta, ya), o);
              break;
            }
            Nu(n, ta, ya);
            break;
          case 5:
            Nu(n, ta, ya);
            break;
          default:
            throw Error(k(329));
        }
      }
    }
    return na(n, Je()), n.callbackNode === l ? uf.bind(null, n) : null;
  }
  function Fs(n, r) {
    var l = Us;
    return n.current.memoizedState.isDehydrated && (el(n, r).flags |= 256), n = of(n, r), n !== 2 && (r = ta, ta = l, r !== null && Lu(r)), n;
  }
  function Lu(n) {
    ta === null ? ta = n : ta.push.apply(ta, n);
  }
  function sy(n) {
    for (var r = n; ; ) {
      if (r.flags & 16384) {
        var l = r.updateQueue;
        if (l !== null && (l = l.stores, l !== null)) for (var o = 0; o < l.length; o++) {
          var c = l[o], d = c.getSnapshot;
          c = c.value;
          try {
            if (!ti(d(), c)) return !1;
          } catch {
            return !1;
          }
        }
      }
      if (l = r.child, r.subtreeFlags & 16384 && l !== null) l.return = r, r = l;
      else {
        if (r === n) break;
        for (; r.sibling === null; ) {
          if (r.return === null || r.return === n) return !0;
          r = r.return;
        }
        r.sibling.return = r.return, r = r.sibling;
      }
    }
    return !0;
  }
  function li(n, r) {
    for (r &= ~af, r &= ~Ro, n.suspendedLanes |= r, n.pingedLanes &= ~r, n = n.expirationTimes; 0 < r; ) {
      var l = 31 - kr(r), o = 1 << l;
      n[l] = -1, r &= ~o;
    }
  }
  function Bd(n) {
    if (Rt & 6) throw Error(k(327));
    bo();
    var r = Za(n, 0);
    if (!(r & 1)) return na(n, Je()), null;
    var l = of(n, r);
    if (n.tag !== 0 && l === 2) {
      var o = gl(n);
      o !== 0 && (r = o, l = Fs(n, o));
    }
    if (l === 1) throw l = zs, el(n, 0), li(n, r), na(n, Je()), l;
    if (l === 6) throw Error(k(345));
    return n.finishedWork = n.current.alternate, n.finishedLanes = r, Nu(n, ta, ya), na(n, Je()), null;
  }
  function Id(n, r) {
    var l = Rt;
    Rt |= 1;
    try {
      return n(r);
    } finally {
      Rt = l, Rt === 0 && (To = Je() + 500, ho && Ti());
    }
  }
  function Mu(n) {
    Ji !== null && Ji.tag === 0 && !(Rt & 6) && bo();
    var r = Rt;
    Rt |= 1;
    var l = or.transition, o = Lt;
    try {
      if (or.transition = null, Lt = 1, n) return n();
    } finally {
      Lt = o, or.transition = l, Rt = r, !(Rt & 6) && Ti();
    }
  }
  function Yd() {
    ma = Co.current, an(Co);
  }
  function el(n, r) {
    n.finishedWork = null, n.finishedLanes = 0;
    var l = n.timeoutHandle;
    if (l !== -1 && (n.timeoutHandle = -1, pd(l)), Fn !== null) for (l = Fn.return; l !== null; ) {
      var o = l;
      switch (_c(o), o.tag) {
        case 1:
          o = o.type.childContextTypes, o != null && vo();
          break;
        case 3:
          Eu(), an($n), an(En), Oe();
          break;
        case 5:
          Lc(o);
          break;
        case 4:
          Eu();
          break;
        case 13:
          an(gn);
          break;
        case 19:
          an(gn);
          break;
        case 10:
          Sd(o.type._context);
          break;
        case 22:
        case 23:
          Yd();
      }
      l = l.return;
    }
    if (Wn = n, Fn = n = Hl(n.current, null), sr = ma = r, _n = 0, zs = null, af = Ro = Oi = 0, ta = Us = null, gu !== null) {
      for (r = 0; r < gu.length; r++) if (l = gu[r], o = l.interleaved, o !== null) {
        l.interleaved = null;
        var c = o.next, d = l.pending;
        if (d !== null) {
          var m = d.next;
          d.next = c, o.next = m;
        }
        l.pending = o;
      }
      gu = null;
    }
    return n;
  }
  function Jv(n, r) {
    do {
      var l = Fn;
      try {
        if (gd(), vt.current = bu, Nc) {
          for (var o = Nt.memoizedState; o !== null; ) {
            var c = o.queue;
            c !== null && (c.pending = null), o = o.next;
          }
          Nc = !1;
        }
        if (Kt = 0, Zn = Un = Nt = null, hs = !1, Cu = 0, Du.current = null, l === null || l.return === null) {
          _n = 1, zs = r, Fn = null;
          break;
        }
        e: {
          var d = n, m = l.return, E = l, T = r;
          if (r = sr, E.flags |= 32768, T !== null && typeof T == "object" && typeof T.then == "function") {
            var U = T, W = E, K = W.tag;
            if (!(W.mode & 1) && (K === 0 || K === 11 || K === 15)) {
              var Q = W.alternate;
              Q ? (W.updateQueue = Q.updateQueue, W.memoizedState = Q.memoizedState, W.lanes = Q.lanes) : (W.updateQueue = null, W.memoizedState = null);
            }
            var fe = Pv(m);
            if (fe !== null) {
              fe.flags &= -257, Ul(fe, m, E, d, r), fe.mode & 1 && Md(d, U, r), r = fe, T = U;
              var me = r.updateQueue;
              if (me === null) {
                var Ce = /* @__PURE__ */ new Set();
                Ce.add(T), r.updateQueue = Ce;
              } else me.add(T);
              break e;
            } else {
              if (!(r & 1)) {
                Md(d, U, r), $d();
                break e;
              }
              T = Error(k(426));
            }
          } else if (dn && E.mode & 1) {
            var kn = Pv(m);
            if (kn !== null) {
              !(kn.flags & 65536) && (kn.flags |= 256), Ul(kn, m, E, d, r), Ki(_u(T, E));
              break e;
            }
          }
          d = T = _u(T, E), _n !== 4 && (_n = 2), Us === null ? Us = [d] : Us.push(d), d = m;
          do {
            switch (d.tag) {
              case 3:
                d.flags |= 65536, r &= -r, d.lanes |= r;
                var D = Hv(d, T, r);
                zv(d, D);
                break e;
              case 1:
                E = T;
                var x = d.type, M = d.stateNode;
                if (!(d.flags & 128) && (typeof x.getDerivedStateFromError == "function" || M !== null && typeof M.componentDidCatch == "function" && (jl === null || !jl.has(M)))) {
                  d.flags |= 65536, r &= -r, d.lanes |= r;
                  var G = Ld(d, E, r);
                  zv(d, G);
                  break e;
                }
            }
            d = d.return;
          } while (d !== null);
        }
        rh(l);
      } catch (ye) {
        r = ye, Fn === l && l !== null && (Fn = l = l.return);
        continue;
      }
      break;
    } while (!0);
  }
  function eh() {
    var n = Al.current;
    return Al.current = bu, n === null ? bu : n;
  }
  function $d() {
    (_n === 0 || _n === 3 || _n === 2) && (_n = 4), Wn === null || !(Oi & 268435455) && !(Ro & 268435455) || li(Wn, sr);
  }
  function of(n, r) {
    var l = Rt;
    Rt |= 2;
    var o = eh();
    (Wn !== n || sr !== r) && (ya = null, el(n, r));
    do
      try {
        cy();
        break;
      } catch (c) {
        Jv(n, c);
      }
    while (!0);
    if (gd(), Rt = l, Al.current = o, Fn !== null) throw Error(k(261));
    return Wn = null, sr = 0, _n;
  }
  function cy() {
    for (; Fn !== null; ) nh(Fn);
  }
  function th() {
    for (; Fn !== null && !Ga(); ) nh(Fn);
  }
  function nh(n) {
    var r = uh(n.alternate, n, ma);
    n.memoizedProps = n.pendingProps, r === null ? rh(n) : Fn = r, Du.current = null;
  }
  function rh(n) {
    var r = n;
    do {
      var l = r.alternate;
      if (n = r.return, r.flags & 32768) {
        if (l = tf(l, r), l !== null) {
          l.flags &= 32767, Fn = l;
          return;
        }
        if (n !== null) n.flags |= 32768, n.subtreeFlags = 0, n.deletions = null;
        else {
          _n = 6, Fn = null;
          return;
        }
      } else if (l = Wv(l, r, ma), l !== null) {
        Fn = l;
        return;
      }
      if (r = r.sibling, r !== null) {
        Fn = r;
        return;
      }
      Fn = r = n;
    } while (r !== null);
    _n === 0 && (_n = 5);
  }
  function Nu(n, r, l) {
    var o = Lt, c = or.transition;
    try {
      or.transition = null, Lt = 1, fy(n, r, l, o);
    } finally {
      or.transition = c, Lt = o;
    }
    return null;
  }
  function fy(n, r, l, o) {
    do
      bo();
    while (Ji !== null);
    if (Rt & 6) throw Error(k(327));
    l = n.finishedWork;
    var c = n.finishedLanes;
    if (l === null) return null;
    if (n.finishedWork = null, n.finishedLanes = 0, l === n.current) throw Error(k(177));
    n.callbackNode = null, n.callbackPriority = 0;
    var d = l.lanes | l.childLanes;
    if (Qf(n, d), n === Wn && (Fn = Wn = null, sr = 0), !(l.subtreeFlags & 2064) && !(l.flags & 2064) || lf || (lf = !0, oh(ru, function() {
      return bo(), null;
    })), d = (l.flags & 15990) !== 0, l.subtreeFlags & 15990 || d) {
      d = or.transition, or.transition = null;
      var m = Lt;
      Lt = 1;
      var E = Rt;
      Rt |= 4, Du.current = null, Kv(n, l), Fd(l, n), lo(pu), ba = !!is, pu = is = null, n.current = l, uy(l), Ka(), Rt = E, Lt = m, or.transition = d;
    } else n.current = l;
    if (lf && (lf = !1, Ji = n, As = c), d = n.pendingLanes, d === 0 && (jl = null), $o(l.stateNode), na(n, Je()), r !== null) for (o = n.onRecoverableError, l = 0; l < r.length; l++) c = r[l], o(c.value, { componentStack: c.stack, digest: c.digest });
    if (wo) throw wo = !1, n = Ou, Ou = null, n;
    return As & 1 && n.tag !== 0 && bo(), d = n.pendingLanes, d & 1 ? n === xo ? Fl++ : (Fl = 0, xo = n) : Fl = 0, Ti(), null;
  }
  function bo() {
    if (Ji !== null) {
      var n = Zu(As), r = or.transition, l = Lt;
      try {
        if (or.transition = null, Lt = 16 > n ? 16 : n, Ji === null) var o = !1;
        else {
          if (n = Ji, Ji = null, As = 0, Rt & 6) throw Error(k(331));
          var c = Rt;
          for (Rt |= 4, ve = n.current; ve !== null; ) {
            var d = ve, m = d.child;
            if (ve.flags & 16) {
              var E = d.deletions;
              if (E !== null) {
                for (var T = 0; T < E.length; T++) {
                  var U = E[T];
                  for (ve = U; ve !== null; ) {
                    var W = ve;
                    switch (W.tag) {
                      case 0:
                      case 11:
                      case 15:
                        Os(8, W, d);
                    }
                    var K = W.child;
                    if (K !== null) K.return = W, ve = K;
                    else for (; ve !== null; ) {
                      W = ve;
                      var Q = W.sibling, fe = W.return;
                      if (rf(W), W === U) {
                        ve = null;
                        break;
                      }
                      if (Q !== null) {
                        Q.return = fe, ve = Q;
                        break;
                      }
                      ve = fe;
                    }
                  }
                }
                var me = d.alternate;
                if (me !== null) {
                  var Ce = me.child;
                  if (Ce !== null) {
                    me.child = null;
                    do {
                      var kn = Ce.sibling;
                      Ce.sibling = null, Ce = kn;
                    } while (Ce !== null);
                  }
                }
                ve = d;
              }
            }
            if (d.subtreeFlags & 2064 && m !== null) m.return = d, ve = m;
            else e: for (; ve !== null; ) {
              if (d = ve, d.flags & 2048) switch (d.tag) {
                case 0:
                case 11:
                case 15:
                  Os(9, d, d.return);
              }
              var D = d.sibling;
              if (D !== null) {
                D.return = d.return, ve = D;
                break e;
              }
              ve = d.return;
            }
          }
          var x = n.current;
          for (ve = x; ve !== null; ) {
            m = ve;
            var M = m.child;
            if (m.subtreeFlags & 2064 && M !== null) M.return = m, ve = M;
            else e: for (m = x; ve !== null; ) {
              if (E = ve, E.flags & 2048) try {
                switch (E.tag) {
                  case 0:
                  case 11:
                  case 15:
                    Ls(9, E);
                }
              } catch (ye) {
                pn(E, E.return, ye);
              }
              if (E === m) {
                ve = null;
                break e;
              }
              var G = E.sibling;
              if (G !== null) {
                G.return = E.return, ve = G;
                break e;
              }
              ve = E.return;
            }
          }
          if (Rt = c, Ti(), $r && typeof $r.onPostCommitFiberRoot == "function") try {
            $r.onPostCommitFiberRoot(ml, n);
          } catch {
          }
          o = !0;
        }
        return o;
      } finally {
        Lt = l, or.transition = r;
      }
    }
    return !1;
  }
  function ah(n, r, l) {
    r = _u(l, r), r = Hv(n, r, 1), n = Ml(n, r, 1), r = Hn(), n !== null && (Pi(n, 1, r), na(n, r));
  }
  function pn(n, r, l) {
    if (n.tag === 3) ah(n, n, l);
    else for (; r !== null; ) {
      if (r.tag === 3) {
        ah(r, n, l);
        break;
      } else if (r.tag === 1) {
        var o = r.stateNode;
        if (typeof r.type.getDerivedStateFromError == "function" || typeof o.componentDidCatch == "function" && (jl === null || !jl.has(o))) {
          n = _u(l, n), n = Ld(r, n, 1), r = Ml(r, n, 1), n = Hn(), r !== null && (Pi(r, 1, n), na(r, n));
          break;
        }
      }
      r = r.return;
    }
  }
  function dy(n, r, l) {
    var o = n.pingCache;
    o !== null && o.delete(r), r = Hn(), n.pingedLanes |= n.suspendedLanes & l, Wn === n && (sr & l) === l && (_n === 4 || _n === 3 && (sr & 130023424) === sr && 500 > Je() - Vd ? el(n, 0) : af |= l), na(n, r);
  }
  function ih(n, r) {
    r === 0 && (n.mode & 1 ? (r = fa, fa <<= 1, !(fa & 130023424) && (fa = 4194304)) : r = 1);
    var l = Hn();
    n = va(n, r), n !== null && (Pi(n, r, l), na(n, l));
  }
  function py(n) {
    var r = n.memoizedState, l = 0;
    r !== null && (l = r.retryLane), ih(n, l);
  }
  function lh(n, r) {
    var l = 0;
    switch (n.tag) {
      case 13:
        var o = n.stateNode, c = n.memoizedState;
        c !== null && (l = c.retryLane);
        break;
      case 19:
        o = n.stateNode;
        break;
      default:
        throw Error(k(314));
    }
    o !== null && o.delete(r), ih(n, l);
  }
  var uh;
  uh = function(n, r, l) {
    if (n !== null) if (n.memoizedProps !== r.pendingProps || $n.current) An = !0;
    else {
      if (!(n.lanes & l) && !(r.flags & 128)) return An = !1, _s(n, r, l);
      An = !!(n.flags & 131072);
    }
    else An = !1, dn && r.flags & 1048576 && Ov(r, Gi, r.index);
    switch (r.lanes = 0, r.tag) {
      case 2:
        var o = r.type;
        Na(n, r), n = r.pendingProps;
        var c = Gr(r, En.current);
        yn(r, l), c = Nl(null, r, o, n, c, l);
        var d = ri();
        return r.flags |= 1, typeof c == "object" && c !== null && typeof c.render == "function" && c.$$typeof === void 0 ? (r.tag = 1, r.memoizedState = null, r.updateQueue = null, Nn(o) ? (d = !0, Xn(r)) : d = !1, r.memoizedState = c.state !== null && c.state !== void 0 ? c.state : null, Td(r), c.updater = qc, r.stateNode = c, c._reactInternals = r, Rs(r, o, n, l), r = xs(null, r, o, !0, d, l)) : (r.tag = 0, dn && d && bc(r), ur(null, r, c, l), r = r.child), r;
      case 16:
        o = r.elementType;
        e: {
          switch (Na(n, r), n = r.pendingProps, c = o._init, o = c(o._payload), r.type = o, c = r.tag = hy(o), n = ai(o, n), c) {
            case 0:
              r = Vv(null, r, o, n, l);
              break e;
            case 1:
              r = Bv(null, r, o, n, l);
              break e;
            case 11:
              r = Jr(null, r, o, n, l);
              break e;
            case 14:
              r = ku(null, r, o, ai(o.type, n), l);
              break e;
          }
          throw Error(k(
            306,
            o,
            ""
          ));
        }
        return r;
      case 0:
        return o = r.type, c = r.pendingProps, c = r.elementType === o ? c : ai(o, c), Vv(n, r, o, c, l);
      case 1:
        return o = r.type, c = r.pendingProps, c = r.elementType === o ? c : ai(o, c), Bv(n, r, o, c, l);
      case 3:
        e: {
          if (So(r), n === null) throw Error(k(387));
          o = r.pendingProps, d = r.memoizedState, c = d.element, Nv(n, r), cs(r, o, null, l);
          var m = r.memoizedState;
          if (o = m.element, d.isDehydrated) if (d = { element: o, isDehydrated: !1, cache: m.cache, pendingSuspenseBoundaries: m.pendingSuspenseBoundaries, transitions: m.transitions }, r.updateQueue.baseState = d, r.memoizedState = d, r.flags & 256) {
            c = _u(Error(k(423)), r), r = Iv(n, r, o, l, c);
            break e;
          } else if (o !== c) {
            c = _u(Error(k(424)), r), r = Iv(n, r, o, l, c);
            break e;
          } else for (qr = Ei(r.stateNode.containerInfo.firstChild), Kr = r, dn = !0, La = null, l = le(r, null, o, l), r.child = l; l; ) l.flags = l.flags & -3 | 4096, l = l.sibling;
          else {
            if (Ll(), o === c) {
              r = za(n, r, l);
              break e;
            }
            ur(n, r, o, l);
          }
          r = r.child;
        }
        return r;
      case 5:
        return Uv(r), n === null && md(r), o = r.type, c = r.pendingProps, d = n !== null ? n.memoizedProps : null, m = c.children, Cc(o, c) ? m = null : d !== null && Cc(o, d) && (r.flags |= 32), Nd(n, r), ur(n, r, m, l), r.child;
      case 6:
        return n === null && md(r), null;
      case 13:
        return ef(n, r, l);
      case 4:
        return xd(r, r.stateNode.containerInfo), o = r.pendingProps, n === null ? r.child = wn(r, null, o, l) : ur(n, r, o, l), r.child;
      case 11:
        return o = r.type, c = r.pendingProps, c = r.elementType === o ? c : ai(o, c), Jr(n, r, o, c, l);
      case 7:
        return ur(n, r, r.pendingProps, l), r.child;
      case 8:
        return ur(n, r, r.pendingProps.children, l), r.child;
      case 12:
        return ur(n, r, r.pendingProps.children, l), r.child;
      case 10:
        e: {
          if (o = r.type._context, c = r.pendingProps, d = r.memoizedProps, m = c.value, _e(pa, o._currentValue), o._currentValue = m, d !== null) if (ti(d.value, m)) {
            if (d.children === c.children && !$n.current) {
              r = za(n, r, l);
              break e;
            }
          } else for (d = r.child, d !== null && (d.return = r); d !== null; ) {
            var E = d.dependencies;
            if (E !== null) {
              m = d.child;
              for (var T = E.firstContext; T !== null; ) {
                if (T.context === o) {
                  if (d.tag === 1) {
                    T = qi(-1, l & -l), T.tag = 2;
                    var U = d.updateQueue;
                    if (U !== null) {
                      U = U.shared;
                      var W = U.pending;
                      W === null ? T.next = T : (T.next = W.next, W.next = T), U.pending = T;
                    }
                  }
                  d.lanes |= l, T = d.alternate, T !== null && (T.lanes |= l), Ed(
                    d.return,
                    l,
                    r
                  ), E.lanes |= l;
                  break;
                }
                T = T.next;
              }
            } else if (d.tag === 10) m = d.type === r.type ? null : d.child;
            else if (d.tag === 18) {
              if (m = d.return, m === null) throw Error(k(341));
              m.lanes |= l, E = m.alternate, E !== null && (E.lanes |= l), Ed(m, l, r), m = d.sibling;
            } else m = d.child;
            if (m !== null) m.return = d;
            else for (m = d; m !== null; ) {
              if (m === r) {
                m = null;
                break;
              }
              if (d = m.sibling, d !== null) {
                d.return = m.return, m = d;
                break;
              }
              m = m.return;
            }
            d = m;
          }
          ur(n, r, c.children, l), r = r.child;
        }
        return r;
      case 9:
        return c = r.type, o = r.pendingProps.children, yn(r, l), c = Ma(c), o = o(c), r.flags |= 1, ur(n, r, o, l), r.child;
      case 14:
        return o = r.type, c = ai(o, r.pendingProps), c = ai(o.type, c), ku(n, r, o, c, l);
      case 15:
        return et(n, r, r.type, r.pendingProps, l);
      case 17:
        return o = r.type, c = r.pendingProps, c = r.elementType === o ? c : ai(o, c), Na(n, r), r.tag = 1, Nn(o) ? (n = !0, Xn(r)) : n = !1, yn(r, l), Xc(r, o, c), Rs(r, o, c, l), xs(null, r, o, !0, n, l);
      case 19:
        return _i(n, r, l);
      case 22:
        return ws(n, r, l);
    }
    throw Error(k(156, r.tag));
  };
  function oh(n, r) {
    return sn(n, r);
  }
  function vy(n, r, l, o) {
    this.tag = n, this.key = l, this.sibling = this.child = this.return = this.stateNode = this.type = this.elementType = null, this.index = 0, this.ref = null, this.pendingProps = r, this.dependencies = this.memoizedState = this.updateQueue = this.memoizedProps = null, this.mode = o, this.subtreeFlags = this.flags = 0, this.deletions = null, this.childLanes = this.lanes = 0, this.alternate = null;
  }
  function Aa(n, r, l, o) {
    return new vy(n, r, l, o);
  }
  function Qd(n) {
    return n = n.prototype, !(!n || !n.isReactComponent);
  }
  function hy(n) {
    if (typeof n == "function") return Qd(n) ? 1 : 0;
    if (n != null) {
      if (n = n.$$typeof, n === _t) return 11;
      if (n === kt) return 14;
    }
    return 2;
  }
  function Hl(n, r) {
    var l = n.alternate;
    return l === null ? (l = Aa(n.tag, r, n.key, n.mode), l.elementType = n.elementType, l.type = n.type, l.stateNode = n.stateNode, l.alternate = n, n.alternate = l) : (l.pendingProps = r, l.type = n.type, l.flags = 0, l.subtreeFlags = 0, l.deletions = null), l.flags = n.flags & 14680064, l.childLanes = n.childLanes, l.lanes = n.lanes, l.child = n.child, l.memoizedProps = n.memoizedProps, l.memoizedState = n.memoizedState, l.updateQueue = n.updateQueue, r = n.dependencies, l.dependencies = r === null ? null : { lanes: r.lanes, firstContext: r.firstContext }, l.sibling = n.sibling, l.index = n.index, l.ref = n.ref, l;
  }
  function Hs(n, r, l, o, c, d) {
    var m = 2;
    if (o = n, typeof n == "function") Qd(n) && (m = 1);
    else if (typeof n == "string") m = 5;
    else e: switch (n) {
      case He:
        return tl(l.children, c, d, r);
      case ln:
        m = 8, c |= 8;
        break;
      case Pt:
        return n = Aa(12, l, r, c | 2), n.elementType = Pt, n.lanes = d, n;
      case Me:
        return n = Aa(13, l, r, c), n.elementType = Me, n.lanes = d, n;
      case Ft:
        return n = Aa(19, l, r, c), n.elementType = Ft, n.lanes = d, n;
      case Re:
        return Pl(l, c, d, r);
      default:
        if (typeof n == "object" && n !== null) switch (n.$$typeof) {
          case Jt:
            m = 10;
            break e;
          case un:
            m = 9;
            break e;
          case _t:
            m = 11;
            break e;
          case kt:
            m = 14;
            break e;
          case Ot:
            m = 16, o = null;
            break e;
        }
        throw Error(k(130, n == null ? n : typeof n, ""));
    }
    return r = Aa(m, l, r, c), r.elementType = n, r.type = o, r.lanes = d, r;
  }
  function tl(n, r, l, o) {
    return n = Aa(7, n, o, r), n.lanes = l, n;
  }
  function Pl(n, r, l, o) {
    return n = Aa(22, n, o, r), n.elementType = Re, n.lanes = l, n.stateNode = { isHidden: !1 }, n;
  }
  function Wd(n, r, l) {
    return n = Aa(6, n, null, r), n.lanes = l, n;
  }
  function sf(n, r, l) {
    return r = Aa(4, n.children !== null ? n.children : [], n.key, r), r.lanes = l, r.stateNode = { containerInfo: n.containerInfo, pendingChildren: null, implementation: n.implementation }, r;
  }
  function sh(n, r, l, o, c) {
    this.tag = r, this.containerInfo = n, this.finishedWork = this.pingCache = this.current = this.pendingChildren = null, this.timeoutHandle = -1, this.callbackNode = this.pendingContext = this.context = null, this.callbackPriority = 0, this.eventTimes = Xu(0), this.expirationTimes = Xu(-1), this.entangledLanes = this.finishedLanes = this.mutableReadLanes = this.expiredLanes = this.pingedLanes = this.suspendedLanes = this.pendingLanes = 0, this.entanglements = Xu(0), this.identifierPrefix = o, this.onRecoverableError = c, this.mutableSourceEagerHydrationData = null;
  }
  function cf(n, r, l, o, c, d, m, E, T) {
    return n = new sh(n, r, l, E, T), r === 1 ? (r = 1, d === !0 && (r |= 8)) : r = 0, d = Aa(3, null, null, r), n.current = d, d.stateNode = n, d.memoizedState = { element: o, isDehydrated: l, cache: null, transitions: null, pendingSuspenseBoundaries: null }, Td(d), n;
  }
  function my(n, r, l) {
    var o = 3 < arguments.length && arguments[3] !== void 0 ? arguments[3] : null;
    return { $$typeof: Qe, key: o == null ? null : "" + o, children: n, containerInfo: r, implementation: l };
  }
  function Gd(n) {
    if (!n) return Cr;
    n = n._reactInternals;
    e: {
      if (Ze(n) !== n || n.tag !== 1) throw Error(k(170));
      var r = n;
      do {
        switch (r.tag) {
          case 3:
            r = r.stateNode.context;
            break e;
          case 1:
            if (Nn(r.type)) {
              r = r.stateNode.__reactInternalMemoizedMergedChildContext;
              break e;
            }
        }
        r = r.return;
      } while (r !== null);
      throw Error(k(171));
    }
    if (n.tag === 1) {
      var l = n.type;
      if (Nn(l)) return os(n, l, r);
    }
    return r;
  }
  function ch(n, r, l, o, c, d, m, E, T) {
    return n = cf(l, o, !0, n, c, d, m, E, T), n.context = Gd(null), l = n.current, o = Hn(), c = Li(l), d = qi(o, c), d.callback = r ?? null, Ml(l, d, c), n.current.lanes = c, Pi(n, c, o), na(n, o), n;
  }
  function ff(n, r, l, o) {
    var c = r.current, d = Hn(), m = Li(c);
    return l = Gd(l), r.context === null ? r.context = l : r.pendingContext = l, r = qi(d, m), r.payload = { element: n }, o = o === void 0 ? null : o, o !== null && (r.callback = o), n = Ml(c, r, m), n !== null && (zr(n, c, m, d), Oc(n, c, m)), m;
  }
  function df(n) {
    if (n = n.current, !n.child) return null;
    switch (n.child.tag) {
      case 5:
        return n.child.stateNode;
      default:
        return n.child.stateNode;
    }
  }
  function Kd(n, r) {
    if (n = n.memoizedState, n !== null && n.dehydrated !== null) {
      var l = n.retryLane;
      n.retryLane = l !== 0 && l < r ? l : r;
    }
  }
  function pf(n, r) {
    Kd(n, r), (n = n.alternate) && Kd(n, r);
  }
  function fh() {
    return null;
  }
  var zu = typeof reportError == "function" ? reportError : function(n) {
    console.error(n);
  };
  function qd(n) {
    this._internalRoot = n;
  }
  vf.prototype.render = qd.prototype.render = function(n) {
    var r = this._internalRoot;
    if (r === null) throw Error(k(409));
    ff(n, r, null, null);
  }, vf.prototype.unmount = qd.prototype.unmount = function() {
    var n = this._internalRoot;
    if (n !== null) {
      this._internalRoot = null;
      var r = n.containerInfo;
      Mu(function() {
        ff(null, n, null, null);
      }), r[Qi] = null;
    }
  };
  function vf(n) {
    this._internalRoot = n;
  }
  vf.prototype.unstable_scheduleHydration = function(n) {
    if (n) {
      var r = We();
      n = { blockedOn: null, target: n, priority: r };
      for (var l = 0; l < Yn.length && r !== 0 && r < Yn[l].priority; l++) ;
      Yn.splice(l, 0, n), l === 0 && Go(n);
    }
  };
  function Xd(n) {
    return !(!n || n.nodeType !== 1 && n.nodeType !== 9 && n.nodeType !== 11);
  }
  function hf(n) {
    return !(!n || n.nodeType !== 1 && n.nodeType !== 9 && n.nodeType !== 11 && (n.nodeType !== 8 || n.nodeValue !== " react-mount-point-unstable "));
  }
  function dh() {
  }
  function yy(n, r, l, o, c) {
    if (c) {
      if (typeof o == "function") {
        var d = o;
        o = function() {
          var U = df(m);
          d.call(U);
        };
      }
      var m = ch(r, o, n, 0, null, !1, !1, "", dh);
      return n._reactRootContainer = m, n[Qi] = m.current, oo(n.nodeType === 8 ? n.parentNode : n), Mu(), m;
    }
    for (; c = n.lastChild; ) n.removeChild(c);
    if (typeof o == "function") {
      var E = o;
      o = function() {
        var U = df(T);
        E.call(U);
      };
    }
    var T = cf(n, 0, !1, null, null, !1, !1, "", dh);
    return n._reactRootContainer = T, n[Qi] = T.current, oo(n.nodeType === 8 ? n.parentNode : n), Mu(function() {
      ff(r, T, l, o);
    }), T;
  }
  function Ps(n, r, l, o, c) {
    var d = l._reactRootContainer;
    if (d) {
      var m = d;
      if (typeof c == "function") {
        var E = c;
        c = function() {
          var T = df(m);
          E.call(T);
        };
      }
      ff(r, m, n, c);
    } else m = yy(l, r, n, c, o);
    return df(m);
  }
  xt = function(n) {
    switch (n.tag) {
      case 3:
        var r = n.stateNode;
        if (r.current.memoizedState.isDehydrated) {
          var l = Xa(r.pendingLanes);
          l !== 0 && (Vi(r, l | 1), na(r, Je()), !(Rt & 6) && (To = Je() + 500, Ti()));
        }
        break;
      case 13:
        Mu(function() {
          var o = va(n, 1);
          if (o !== null) {
            var c = Hn();
            zr(o, n, 1, c);
          }
        }), pf(n, 1);
    }
  }, Qo = function(n) {
    if (n.tag === 13) {
      var r = va(n, 134217728);
      if (r !== null) {
        var l = Hn();
        zr(r, n, 134217728, l);
      }
      pf(n, 134217728);
    }
  }, hi = function(n) {
    if (n.tag === 13) {
      var r = Li(n), l = va(n, r);
      if (l !== null) {
        var o = Hn();
        zr(l, n, r, o);
      }
      pf(n, r);
    }
  }, We = function() {
    return Lt;
  }, Ju = function(n, r) {
    var l = Lt;
    try {
      return Lt = n, r();
    } finally {
      Lt = l;
    }
  }, $t = function(n, r, l) {
    switch (r) {
      case "input":
        if (Yr(n, l), r = l.name, l.type === "radio" && r != null) {
          for (l = n; l.parentNode; ) l = l.parentNode;
          for (l = l.querySelectorAll("input[name=" + JSON.stringify("" + r) + '][type="radio"]'), r = 0; r < l.length; r++) {
            var o = l[r];
            if (o !== n && o.form === n.form) {
              var c = mn(o);
              if (!c) throw Error(k(90));
              xr(o), Yr(o, c);
            }
          }
        }
        break;
      case "textarea":
        $a(n, l);
        break;
      case "select":
        r = l.value, r != null && Rn(n, !!l.multiple, r, !1);
    }
  }, eu = Id, pl = Mu;
  var gy = { usingClientEntryPoint: !1, Events: [De, ni, mn, Hi, Jl, Id] }, Vs = { findFiberByHostInstance: vu, bundleType: 0, version: "18.3.1", rendererPackageName: "react-dom" }, ph = { bundleType: Vs.bundleType, version: Vs.version, rendererPackageName: Vs.rendererPackageName, rendererConfig: Vs.rendererConfig, overrideHookState: null, overrideHookStateDeletePath: null, overrideHookStateRenamePath: null, overrideProps: null, overridePropsDeletePath: null, overridePropsRenamePath: null, setErrorHandler: null, setSuspenseHandler: null, scheduleUpdate: null, currentDispatcherRef: it.ReactCurrentDispatcher, findHostInstanceByFiber: function(n) {
    return n = Tn(n), n === null ? null : n.stateNode;
  }, findFiberByHostInstance: Vs.findFiberByHostInstance || fh, findHostInstancesForRefresh: null, scheduleRefresh: null, scheduleRoot: null, setRefreshHandler: null, getCurrentFiber: null, reconcilerVersion: "18.3.1-next-f1338f8080-20240426" };
  if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u") {
    var Vl = __REACT_DEVTOOLS_GLOBAL_HOOK__;
    if (!Vl.isDisabled && Vl.supportsFiber) try {
      ml = Vl.inject(ph), $r = Vl;
    } catch {
    }
  }
  return Ba.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = gy, Ba.createPortal = function(n, r) {
    var l = 2 < arguments.length && arguments[2] !== void 0 ? arguments[2] : null;
    if (!Xd(r)) throw Error(k(200));
    return my(n, r, null, l);
  }, Ba.createRoot = function(n, r) {
    if (!Xd(n)) throw Error(k(299));
    var l = !1, o = "", c = zu;
    return r != null && (r.unstable_strictMode === !0 && (l = !0), r.identifierPrefix !== void 0 && (o = r.identifierPrefix), r.onRecoverableError !== void 0 && (c = r.onRecoverableError)), r = cf(n, 1, !1, null, null, l, !1, o, c), n[Qi] = r.current, oo(n.nodeType === 8 ? n.parentNode : n), new qd(r);
  }, Ba.findDOMNode = function(n) {
    if (n == null) return null;
    if (n.nodeType === 1) return n;
    var r = n._reactInternals;
    if (r === void 0)
      throw typeof n.render == "function" ? Error(k(188)) : (n = Object.keys(n).join(","), Error(k(268, n)));
    return n = Tn(r), n = n === null ? null : n.stateNode, n;
  }, Ba.flushSync = function(n) {
    return Mu(n);
  }, Ba.hydrate = function(n, r, l) {
    if (!hf(r)) throw Error(k(200));
    return Ps(null, n, r, !0, l);
  }, Ba.hydrateRoot = function(n, r, l) {
    if (!Xd(n)) throw Error(k(405));
    var o = l != null && l.hydratedSources || null, c = !1, d = "", m = zu;
    if (l != null && (l.unstable_strictMode === !0 && (c = !0), l.identifierPrefix !== void 0 && (d = l.identifierPrefix), l.onRecoverableError !== void 0 && (m = l.onRecoverableError)), r = ch(r, null, n, 1, l ?? null, c, !1, d, m), n[Qi] = r.current, oo(n), o) for (n = 0; n < o.length; n++) l = o[n], c = l._getVersion, c = c(l._source), r.mutableSourceEagerHydrationData == null ? r.mutableSourceEagerHydrationData = [l, c] : r.mutableSourceEagerHydrationData.push(
      l,
      c
    );
    return new vf(r);
  }, Ba.render = function(n, r, l) {
    if (!hf(r)) throw Error(k(200));
    return Ps(null, n, r, !1, l);
  }, Ba.unmountComponentAtNode = function(n) {
    if (!hf(n)) throw Error(k(40));
    return n._reactRootContainer ? (Mu(function() {
      Ps(null, null, n, !1, function() {
        n._reactRootContainer = null, n[Qi] = null;
      });
    }), !0) : !1;
  }, Ba.unstable_batchedUpdates = Id, Ba.unstable_renderSubtreeIntoContainer = function(n, r, l, o) {
    if (!hf(l)) throw Error(k(200));
    if (n == null || n._reactInternals === void 0) throw Error(k(38));
    return Ps(n, r, l, !1, o);
  }, Ba.version = "18.3.1-next-f1338f8080-20240426", Ba;
}
var Ia = {};
/**
 * @license React
 * react-dom.development.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var rT;
function ak() {
  return rT || (rT = 1, process.env.NODE_ENV !== "production" && function() {
    typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart == "function" && __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart(new Error());
    var I = Ya, j = lT(), k = I.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED, Te = !1;
    function Fe(e) {
      Te = e;
    }
    function Ee(e) {
      if (!Te) {
        for (var t = arguments.length, a = new Array(t > 1 ? t - 1 : 0), i = 1; i < t; i++)
          a[i - 1] = arguments[i];
        Et("warn", e, a);
      }
    }
    function S(e) {
      if (!Te) {
        for (var t = arguments.length, a = new Array(t > 1 ? t - 1 : 0), i = 1; i < t; i++)
          a[i - 1] = arguments[i];
        Et("error", e, a);
      }
    }
    function Et(e, t, a) {
      {
        var i = k.ReactDebugCurrentFrame, u = i.getStackAddendum();
        u !== "" && (t += "%s", a = a.concat([u]));
        var s = a.map(function(f) {
          return String(f);
        });
        s.unshift("Warning: " + t), Function.prototype.apply.call(console[e], console, s);
      }
    }
    var se = 0, ce = 1, tt = 2, J = 3, Se = 4, ae = 5, Ve = 6, at = 7, ct = 8, gt = 9, qe = 10, Le = 11, it = 12, ke = 13, Qe = 14, He = 15, ln = 16, Pt = 17, Jt = 18, un = 19, _t = 21, Me = 22, Ft = 23, kt = 24, Ot = 25, Re = !0, Z = !1, we = !1, ne = !1, _ = !1, V = !0, Ie = !0, Pe = !0, ft = !0, lt = /* @__PURE__ */ new Set(), nt = {}, ut = {};
    function dt(e, t) {
      It(e, t), It(e + "Capture", t);
    }
    function It(e, t) {
      nt[e] && S("EventRegistry: More than one plugin attempted to publish the same registration name, `%s`.", e), nt[e] = t;
      {
        var a = e.toLowerCase();
        ut[a] = e, e === "onDoubleClick" && (ut.ondblclick = e);
      }
      for (var i = 0; i < t.length; i++)
        lt.add(t[i]);
    }
    var On = typeof window < "u" && typeof window.document < "u" && typeof window.document.createElement < "u", xr = Object.prototype.hasOwnProperty;
    function Cn(e) {
      {
        var t = typeof Symbol == "function" && Symbol.toStringTag, a = t && e[Symbol.toStringTag] || e.constructor.name || "Object";
        return a;
      }
    }
    function nr(e) {
      try {
        return Vn(e), !1;
      } catch {
        return !0;
      }
    }
    function Vn(e) {
      return "" + e;
    }
    function Bn(e, t) {
      if (nr(e))
        return S("The provided `%s` attribute is an unsupported type %s. This value must be coerced to a string before before using it here.", t, Cn(e)), Vn(e);
    }
    function Yr(e) {
      if (nr(e))
        return S("The provided key is an unsupported type %s. This value must be coerced to a string before before using it here.", Cn(e)), Vn(e);
    }
    function ci(e, t) {
      if (nr(e))
        return S("The provided `%s` prop is an unsupported type %s. This value must be coerced to a string before before using it here.", t, Cn(e)), Vn(e);
    }
    function oa(e, t) {
      if (nr(e))
        return S("The provided `%s` CSS property is an unsupported type %s. This value must be coerced to a string before before using it here.", t, Cn(e)), Vn(e);
    }
    function Kn(e) {
      if (nr(e))
        return S("The provided HTML markup uses a value of unsupported type %s. This value must be coerced to a string before before using it here.", Cn(e)), Vn(e);
    }
    function Rn(e) {
      if (nr(e))
        return S("Form field values (value, checked, defaultValue, or defaultChecked props) must be strings, not %s. This value must be coerced to a string before before using it here.", Cn(e)), Vn(e);
    }
    var In = 0, gr = 1, $a = 2, Ln = 3, Sr = 4, sa = 5, Qa = 6, fi = ":A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD", ee = fi + "\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040", xe = new RegExp("^[" + fi + "][" + ee + "]*$"), ot = {}, Ht = {};
    function en(e) {
      return xr.call(Ht, e) ? !0 : xr.call(ot, e) ? !1 : xe.test(e) ? (Ht[e] = !0, !0) : (ot[e] = !0, S("Invalid attribute name: `%s`", e), !1);
    }
    function vn(e, t, a) {
      return t !== null ? t.type === In : a ? !1 : e.length > 2 && (e[0] === "o" || e[0] === "O") && (e[1] === "n" || e[1] === "N");
    }
    function on(e, t, a, i) {
      if (a !== null && a.type === In)
        return !1;
      switch (typeof t) {
        case "function":
        case "symbol":
          return !0;
        case "boolean": {
          if (i)
            return !1;
          if (a !== null)
            return !a.acceptsBooleans;
          var u = e.toLowerCase().slice(0, 5);
          return u !== "data-" && u !== "aria-";
        }
        default:
          return !1;
      }
    }
    function qn(e, t, a, i) {
      if (t === null || typeof t > "u" || on(e, t, a, i))
        return !0;
      if (i)
        return !1;
      if (a !== null)
        switch (a.type) {
          case Ln:
            return !t;
          case Sr:
            return t === !1;
          case sa:
            return isNaN(t);
          case Qa:
            return isNaN(t) || t < 1;
        }
      return !1;
    }
    function tn(e) {
      return $t.hasOwnProperty(e) ? $t[e] : null;
    }
    function Yt(e, t, a, i, u, s, f) {
      this.acceptsBooleans = t === $a || t === Ln || t === Sr, this.attributeName = i, this.attributeNamespace = u, this.mustUseProperty = a, this.propertyName = e, this.type = t, this.sanitizeURL = s, this.removeEmptyString = f;
    }
    var $t = {}, ca = [
      "children",
      "dangerouslySetInnerHTML",
      // TODO: This prevents the assignment of defaultValue to regular
      // elements (not just inputs). Now that ReactDOMInput assigns to the
      // defaultValue property -- do we need this?
      "defaultValue",
      "defaultChecked",
      "innerHTML",
      "suppressContentEditableWarning",
      "suppressHydrationWarning",
      "style"
    ];
    ca.forEach(function(e) {
      $t[e] = new Yt(
        e,
        In,
        !1,
        // mustUseProperty
        e,
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    }), [["acceptCharset", "accept-charset"], ["className", "class"], ["htmlFor", "for"], ["httpEquiv", "http-equiv"]].forEach(function(e) {
      var t = e[0], a = e[1];
      $t[t] = new Yt(
        t,
        gr,
        !1,
        // mustUseProperty
        a,
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    }), ["contentEditable", "draggable", "spellCheck", "value"].forEach(function(e) {
      $t[e] = new Yt(
        e,
        $a,
        !1,
        // mustUseProperty
        e.toLowerCase(),
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    }), ["autoReverse", "externalResourcesRequired", "focusable", "preserveAlpha"].forEach(function(e) {
      $t[e] = new Yt(
        e,
        $a,
        !1,
        // mustUseProperty
        e,
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    }), [
      "allowFullScreen",
      "async",
      // Note: there is a special case that prevents it from being written to the DOM
      // on the client side because the browsers are inconsistent. Instead we call focus().
      "autoFocus",
      "autoPlay",
      "controls",
      "default",
      "defer",
      "disabled",
      "disablePictureInPicture",
      "disableRemotePlayback",
      "formNoValidate",
      "hidden",
      "loop",
      "noModule",
      "noValidate",
      "open",
      "playsInline",
      "readOnly",
      "required",
      "reversed",
      "scoped",
      "seamless",
      // Microdata
      "itemScope"
    ].forEach(function(e) {
      $t[e] = new Yt(
        e,
        Ln,
        !1,
        // mustUseProperty
        e.toLowerCase(),
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    }), [
      "checked",
      // Note: `option.selected` is not updated if `select.multiple` is
      // disabled with `removeAttribute`. We have special logic for handling this.
      "multiple",
      "muted",
      "selected"
      // NOTE: if you add a camelCased prop to this list,
      // you'll need to set attributeName to name.toLowerCase()
      // instead in the assignment below.
    ].forEach(function(e) {
      $t[e] = new Yt(
        e,
        Ln,
        !0,
        // mustUseProperty
        e,
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    }), [
      "capture",
      "download"
      // NOTE: if you add a camelCased prop to this list,
      // you'll need to set attributeName to name.toLowerCase()
      // instead in the assignment below.
    ].forEach(function(e) {
      $t[e] = new Yt(
        e,
        Sr,
        !1,
        // mustUseProperty
        e,
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    }), [
      "cols",
      "rows",
      "size",
      "span"
      // NOTE: if you add a camelCased prop to this list,
      // you'll need to set attributeName to name.toLowerCase()
      // instead in the assignment below.
    ].forEach(function(e) {
      $t[e] = new Yt(
        e,
        Qa,
        !1,
        // mustUseProperty
        e,
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    }), ["rowSpan", "start"].forEach(function(e) {
      $t[e] = new Yt(
        e,
        sa,
        !1,
        // mustUseProperty
        e.toLowerCase(),
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    });
    var Er = /[\-\:]([a-z])/g, Ta = function(e) {
      return e[1].toUpperCase();
    };
    [
      "accent-height",
      "alignment-baseline",
      "arabic-form",
      "baseline-shift",
      "cap-height",
      "clip-path",
      "clip-rule",
      "color-interpolation",
      "color-interpolation-filters",
      "color-profile",
      "color-rendering",
      "dominant-baseline",
      "enable-background",
      "fill-opacity",
      "fill-rule",
      "flood-color",
      "flood-opacity",
      "font-family",
      "font-size",
      "font-size-adjust",
      "font-stretch",
      "font-style",
      "font-variant",
      "font-weight",
      "glyph-name",
      "glyph-orientation-horizontal",
      "glyph-orientation-vertical",
      "horiz-adv-x",
      "horiz-origin-x",
      "image-rendering",
      "letter-spacing",
      "lighting-color",
      "marker-end",
      "marker-mid",
      "marker-start",
      "overline-position",
      "overline-thickness",
      "paint-order",
      "panose-1",
      "pointer-events",
      "rendering-intent",
      "shape-rendering",
      "stop-color",
      "stop-opacity",
      "strikethrough-position",
      "strikethrough-thickness",
      "stroke-dasharray",
      "stroke-dashoffset",
      "stroke-linecap",
      "stroke-linejoin",
      "stroke-miterlimit",
      "stroke-opacity",
      "stroke-width",
      "text-anchor",
      "text-decoration",
      "text-rendering",
      "underline-position",
      "underline-thickness",
      "unicode-bidi",
      "unicode-range",
      "units-per-em",
      "v-alphabetic",
      "v-hanging",
      "v-ideographic",
      "v-mathematical",
      "vector-effect",
      "vert-adv-y",
      "vert-origin-x",
      "vert-origin-y",
      "word-spacing",
      "writing-mode",
      "xmlns:xlink",
      "x-height"
      // NOTE: if you add a camelCased prop to this list,
      // you'll need to set attributeName to name.toLowerCase()
      // instead in the assignment below.
    ].forEach(function(e) {
      var t = e.replace(Er, Ta);
      $t[t] = new Yt(
        t,
        gr,
        !1,
        // mustUseProperty
        e,
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    }), [
      "xlink:actuate",
      "xlink:arcrole",
      "xlink:role",
      "xlink:show",
      "xlink:title",
      "xlink:type"
      // NOTE: if you add a camelCased prop to this list,
      // you'll need to set attributeName to name.toLowerCase()
      // instead in the assignment below.
    ].forEach(function(e) {
      var t = e.replace(Er, Ta);
      $t[t] = new Yt(
        t,
        gr,
        !1,
        // mustUseProperty
        e,
        "http://www.w3.org/1999/xlink",
        !1,
        // sanitizeURL
        !1
      );
    }), [
      "xml:base",
      "xml:lang",
      "xml:space"
      // NOTE: if you add a camelCased prop to this list,
      // you'll need to set attributeName to name.toLowerCase()
      // instead in the assignment below.
    ].forEach(function(e) {
      var t = e.replace(Er, Ta);
      $t[t] = new Yt(
        t,
        gr,
        !1,
        // mustUseProperty
        e,
        "http://www.w3.org/XML/1998/namespace",
        !1,
        // sanitizeURL
        !1
      );
    }), ["tabIndex", "crossOrigin"].forEach(function(e) {
      $t[e] = new Yt(
        e,
        gr,
        !1,
        // mustUseProperty
        e.toLowerCase(),
        // attributeName
        null,
        // attributeNamespace
        !1,
        // sanitizeURL
        !1
      );
    });
    var Hi = "xlinkHref";
    $t[Hi] = new Yt(
      "xlinkHref",
      gr,
      !1,
      // mustUseProperty
      "xlink:href",
      "http://www.w3.org/1999/xlink",
      !0,
      // sanitizeURL
      !1
    ), ["src", "href", "action", "formAction"].forEach(function(e) {
      $t[e] = new Yt(
        e,
        gr,
        !1,
        // mustUseProperty
        e.toLowerCase(),
        // attributeName
        null,
        // attributeNamespace
        !0,
        // sanitizeURL
        !0
      );
    });
    var Jl = /^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*\:/i, eu = !1;
    function pl(e) {
      !eu && Jl.test(e) && (eu = !0, S("A future version of React will block javascript: URLs as a security precaution. Use event handlers instead if you can. If you need to generate unsafe HTML try using dangerouslySetInnerHTML instead. React was passed %s.", JSON.stringify(e)));
    }
    function vl(e, t, a, i) {
      if (i.mustUseProperty) {
        var u = i.propertyName;
        return e[u];
      } else {
        Bn(a, t), i.sanitizeURL && pl("" + a);
        var s = i.attributeName, f = null;
        if (i.type === Sr) {
          if (e.hasAttribute(s)) {
            var p = e.getAttribute(s);
            return p === "" ? !0 : qn(t, a, i, !1) ? p : p === "" + a ? a : p;
          }
        } else if (e.hasAttribute(s)) {
          if (qn(t, a, i, !1))
            return e.getAttribute(s);
          if (i.type === Ln)
            return a;
          f = e.getAttribute(s);
        }
        return qn(t, a, i, !1) ? f === null ? a : f : f === "" + a ? a : f;
      }
    }
    function tu(e, t, a, i) {
      {
        if (!en(t))
          return;
        if (!e.hasAttribute(t))
          return a === void 0 ? void 0 : null;
        var u = e.getAttribute(t);
        return Bn(a, t), u === "" + a ? a : u;
      }
    }
    function br(e, t, a, i) {
      var u = tn(t);
      if (!vn(t, u, i)) {
        if (qn(t, a, u, i) && (a = null), i || u === null) {
          if (en(t)) {
            var s = t;
            a === null ? e.removeAttribute(s) : (Bn(a, t), e.setAttribute(s, "" + a));
          }
          return;
        }
        var f = u.mustUseProperty;
        if (f) {
          var p = u.propertyName;
          if (a === null) {
            var v = u.type;
            e[p] = v === Ln ? !1 : "";
          } else
            e[p] = a;
          return;
        }
        var y = u.attributeName, g = u.attributeNamespace;
        if (a === null)
          e.removeAttribute(y);
        else {
          var b = u.type, w;
          b === Ln || b === Sr && a === !0 ? w = "" : (Bn(a, y), w = "" + a, u.sanitizeURL && pl(w.toString())), g ? e.setAttributeNS(g, y, w) : e.setAttribute(y, w);
        }
      }
    }
    var _r = Symbol.for("react.element"), rr = Symbol.for("react.portal"), di = Symbol.for("react.fragment"), Wa = Symbol.for("react.strict_mode"), pi = Symbol.for("react.profiler"), vi = Symbol.for("react.provider"), R = Symbol.for("react.context"), Y = Symbol.for("react.forward_ref"), ie = Symbol.for("react.suspense"), he = Symbol.for("react.suspense_list"), Ze = Symbol.for("react.memo"), Ge = Symbol.for("react.lazy"), ht = Symbol.for("react.scope"), pt = Symbol.for("react.debug_trace_mode"), Tn = Symbol.for("react.offscreen"), nn = Symbol.for("react.legacy_hidden"), sn = Symbol.for("react.cache"), ar = Symbol.for("react.tracing_marker"), Ga = Symbol.iterator, Ka = "@@iterator";
    function Je(e) {
      if (e === null || typeof e != "object")
        return null;
      var t = Ga && e[Ga] || e[Ka];
      return typeof t == "function" ? t : null;
    }
    var rt = Object.assign, qa = 0, nu, ru, hl, Wu, ml, $r, $o;
    function kr() {
    }
    kr.__reactDisabledLog = !0;
    function lc() {
      {
        if (qa === 0) {
          nu = console.log, ru = console.info, hl = console.warn, Wu = console.error, ml = console.group, $r = console.groupCollapsed, $o = console.groupEnd;
          var e = {
            configurable: !0,
            enumerable: !0,
            value: kr,
            writable: !0
          };
          Object.defineProperties(console, {
            info: e,
            log: e,
            warn: e,
            error: e,
            group: e,
            groupCollapsed: e,
            groupEnd: e
          });
        }
        qa++;
      }
    }
    function uc() {
      {
        if (qa--, qa === 0) {
          var e = {
            configurable: !0,
            enumerable: !0,
            writable: !0
          };
          Object.defineProperties(console, {
            log: rt({}, e, {
              value: nu
            }),
            info: rt({}, e, {
              value: ru
            }),
            warn: rt({}, e, {
              value: hl
            }),
            error: rt({}, e, {
              value: Wu
            }),
            group: rt({}, e, {
              value: ml
            }),
            groupCollapsed: rt({}, e, {
              value: $r
            }),
            groupEnd: rt({}, e, {
              value: $o
            })
          });
        }
        qa < 0 && S("disabledDepth fell below zero. This is a bug in React. Please file an issue.");
      }
    }
    var Gu = k.ReactCurrentDispatcher, yl;
    function fa(e, t, a) {
      {
        if (yl === void 0)
          try {
            throw Error();
          } catch (u) {
            var i = u.stack.trim().match(/\n( *(at )?)/);
            yl = i && i[1] || "";
          }
        return `
` + yl + e;
      }
    }
    var Xa = !1, Za;
    {
      var Ku = typeof WeakMap == "function" ? WeakMap : Map;
      Za = new Ku();
    }
    function au(e, t) {
      if (!e || Xa)
        return "";
      {
        var a = Za.get(e);
        if (a !== void 0)
          return a;
      }
      var i;
      Xa = !0;
      var u = Error.prepareStackTrace;
      Error.prepareStackTrace = void 0;
      var s;
      s = Gu.current, Gu.current = null, lc();
      try {
        if (t) {
          var f = function() {
            throw Error();
          };
          if (Object.defineProperty(f.prototype, "props", {
            set: function() {
              throw Error();
            }
          }), typeof Reflect == "object" && Reflect.construct) {
            try {
              Reflect.construct(f, []);
            } catch (A) {
              i = A;
            }
            Reflect.construct(e, [], f);
          } else {
            try {
              f.call();
            } catch (A) {
              i = A;
            }
            e.call(f.prototype);
          }
        } else {
          try {
            throw Error();
          } catch (A) {
            i = A;
          }
          e();
        }
      } catch (A) {
        if (A && i && typeof A.stack == "string") {
          for (var p = A.stack.split(`
`), v = i.stack.split(`
`), y = p.length - 1, g = v.length - 1; y >= 1 && g >= 0 && p[y] !== v[g]; )
            g--;
          for (; y >= 1 && g >= 0; y--, g--)
            if (p[y] !== v[g]) {
              if (y !== 1 || g !== 1)
                do
                  if (y--, g--, g < 0 || p[y] !== v[g]) {
                    var b = `
` + p[y].replace(" at new ", " at ");
                    return e.displayName && b.includes("<anonymous>") && (b = b.replace("<anonymous>", e.displayName)), typeof e == "function" && Za.set(e, b), b;
                  }
                while (y >= 1 && g >= 0);
              break;
            }
        }
      } finally {
        Xa = !1, Gu.current = s, uc(), Error.prepareStackTrace = u;
      }
      var w = e ? e.displayName || e.name : "", N = w ? fa(w) : "";
      return typeof e == "function" && Za.set(e, N), N;
    }
    function gl(e, t, a) {
      return au(e, !0);
    }
    function qu(e, t, a) {
      return au(e, !1);
    }
    function Xu(e) {
      var t = e.prototype;
      return !!(t && t.isReactComponent);
    }
    function Pi(e, t, a) {
      if (e == null)
        return "";
      if (typeof e == "function")
        return au(e, Xu(e));
      if (typeof e == "string")
        return fa(e);
      switch (e) {
        case ie:
          return fa("Suspense");
        case he:
          return fa("SuspenseList");
      }
      if (typeof e == "object")
        switch (e.$$typeof) {
          case Y:
            return qu(e.render);
          case Ze:
            return Pi(e.type, t, a);
          case Ge: {
            var i = e, u = i._payload, s = i._init;
            try {
              return Pi(s(u), t, a);
            } catch {
            }
          }
        }
      return "";
    }
    function Qf(e) {
      switch (e._debugOwner && e._debugOwner.type, e._debugSource, e.tag) {
        case ae:
          return fa(e.type);
        case ln:
          return fa("Lazy");
        case ke:
          return fa("Suspense");
        case un:
          return fa("SuspenseList");
        case se:
        case tt:
        case He:
          return qu(e.type);
        case Le:
          return qu(e.type.render);
        case ce:
          return gl(e.type);
        default:
          return "";
      }
    }
    function Vi(e) {
      try {
        var t = "", a = e;
        do
          t += Qf(a), a = a.return;
        while (a);
        return t;
      } catch (i) {
        return `
Error generating stack: ` + i.message + `
` + i.stack;
      }
    }
    function Lt(e, t, a) {
      var i = e.displayName;
      if (i)
        return i;
      var u = t.displayName || t.name || "";
      return u !== "" ? a + "(" + u + ")" : a;
    }
    function Zu(e) {
      return e.displayName || "Context";
    }
    function xt(e) {
      if (e == null)
        return null;
      if (typeof e.tag == "number" && S("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue."), typeof e == "function")
        return e.displayName || e.name || null;
      if (typeof e == "string")
        return e;
      switch (e) {
        case di:
          return "Fragment";
        case rr:
          return "Portal";
        case pi:
          return "Profiler";
        case Wa:
          return "StrictMode";
        case ie:
          return "Suspense";
        case he:
          return "SuspenseList";
      }
      if (typeof e == "object")
        switch (e.$$typeof) {
          case R:
            var t = e;
            return Zu(t) + ".Consumer";
          case vi:
            var a = e;
            return Zu(a._context) + ".Provider";
          case Y:
            return Lt(e, e.render, "ForwardRef");
          case Ze:
            var i = e.displayName || null;
            return i !== null ? i : xt(e.type) || "Memo";
          case Ge: {
            var u = e, s = u._payload, f = u._init;
            try {
              return xt(f(s));
            } catch {
              return null;
            }
          }
        }
      return null;
    }
    function Qo(e, t, a) {
      var i = t.displayName || t.name || "";
      return e.displayName || (i !== "" ? a + "(" + i + ")" : a);
    }
    function hi(e) {
      return e.displayName || "Context";
    }
    function We(e) {
      var t = e.tag, a = e.type;
      switch (t) {
        case kt:
          return "Cache";
        case gt:
          var i = a;
          return hi(i) + ".Consumer";
        case qe:
          var u = a;
          return hi(u._context) + ".Provider";
        case Jt:
          return "DehydratedFragment";
        case Le:
          return Qo(a, a.render, "ForwardRef");
        case at:
          return "Fragment";
        case ae:
          return a;
        case Se:
          return "Portal";
        case J:
          return "Root";
        case Ve:
          return "Text";
        case ln:
          return xt(a);
        case ct:
          return a === Wa ? "StrictMode" : "Mode";
        case Me:
          return "Offscreen";
        case it:
          return "Profiler";
        case _t:
          return "Scope";
        case ke:
          return "Suspense";
        case un:
          return "SuspenseList";
        case Ot:
          return "TracingMarker";
        case ce:
        case se:
        case Pt:
        case tt:
        case Qe:
        case He:
          if (typeof a == "function")
            return a.displayName || a.name || null;
          if (typeof a == "string")
            return a;
          break;
      }
      return null;
    }
    var Ju = k.ReactDebugCurrentFrame, ir = null, mi = !1;
    function Dr() {
      {
        if (ir === null)
          return null;
        var e = ir._debugOwner;
        if (e !== null && typeof e < "u")
          return We(e);
      }
      return null;
    }
    function yi() {
      return ir === null ? "" : Vi(ir);
    }
    function cn() {
      Ju.getCurrentStack = null, ir = null, mi = !1;
    }
    function Qt(e) {
      Ju.getCurrentStack = e === null ? null : yi, ir = e, mi = !1;
    }
    function Sl() {
      return ir;
    }
    function Yn(e) {
      mi = e;
    }
    function Or(e) {
      return "" + e;
    }
    function wa(e) {
      switch (typeof e) {
        case "boolean":
        case "number":
        case "string":
        case "undefined":
          return e;
        case "object":
          return Rn(e), e;
        default:
          return "";
      }
    }
    var iu = {
      button: !0,
      checkbox: !0,
      image: !0,
      hidden: !0,
      radio: !0,
      reset: !0,
      submit: !0
    };
    function Wo(e, t) {
      iu[t.type] || t.onChange || t.onInput || t.readOnly || t.disabled || t.value == null || S("You provided a `value` prop to a form field without an `onChange` handler. This will render a read-only field. If the field should be mutable use `defaultValue`. Otherwise, set either `onChange` or `readOnly`."), t.onChange || t.readOnly || t.disabled || t.checked == null || S("You provided a `checked` prop to a form field without an `onChange` handler. This will render a read-only field. If the field should be mutable use `defaultChecked`. Otherwise, set either `onChange` or `readOnly`.");
    }
    function Go(e) {
      var t = e.type, a = e.nodeName;
      return a && a.toLowerCase() === "input" && (t === "checkbox" || t === "radio");
    }
    function El(e) {
      return e._valueTracker;
    }
    function lu(e) {
      e._valueTracker = null;
    }
    function Wf(e) {
      var t = "";
      return e && (Go(e) ? t = e.checked ? "true" : "false" : t = e.value), t;
    }
    function xa(e) {
      var t = Go(e) ? "checked" : "value", a = Object.getOwnPropertyDescriptor(e.constructor.prototype, t);
      Rn(e[t]);
      var i = "" + e[t];
      if (!(e.hasOwnProperty(t) || typeof a > "u" || typeof a.get != "function" || typeof a.set != "function")) {
        var u = a.get, s = a.set;
        Object.defineProperty(e, t, {
          configurable: !0,
          get: function() {
            return u.call(this);
          },
          set: function(p) {
            Rn(p), i = "" + p, s.call(this, p);
          }
        }), Object.defineProperty(e, t, {
          enumerable: a.enumerable
        });
        var f = {
          getValue: function() {
            return i;
          },
          setValue: function(p) {
            Rn(p), i = "" + p;
          },
          stopTracking: function() {
            lu(e), delete e[t];
          }
        };
        return f;
      }
    }
    function Ja(e) {
      El(e) || (e._valueTracker = xa(e));
    }
    function gi(e) {
      if (!e)
        return !1;
      var t = El(e);
      if (!t)
        return !0;
      var a = t.getValue(), i = Wf(e);
      return i !== a ? (t.setValue(i), !0) : !1;
    }
    function ba(e) {
      if (e = e || (typeof document < "u" ? document : void 0), typeof e > "u")
        return null;
      try {
        return e.activeElement || e.body;
      } catch {
        return e.body;
      }
    }
    var eo = !1, to = !1, Cl = !1, uu = !1;
    function no(e) {
      var t = e.type === "checkbox" || e.type === "radio";
      return t ? e.checked != null : e.value != null;
    }
    function ro(e, t) {
      var a = e, i = t.checked, u = rt({}, t, {
        defaultChecked: void 0,
        defaultValue: void 0,
        value: void 0,
        checked: i ?? a._wrapperState.initialChecked
      });
      return u;
    }
    function ei(e, t) {
      Wo("input", t), t.checked !== void 0 && t.defaultChecked !== void 0 && !to && (S("%s contains an input of type %s with both checked and defaultChecked props. Input elements must be either controlled or uncontrolled (specify either the checked prop, or the defaultChecked prop, but not both). Decide between using a controlled or uncontrolled input element and remove one of these props. More info: https://reactjs.org/link/controlled-components", Dr() || "A component", t.type), to = !0), t.value !== void 0 && t.defaultValue !== void 0 && !eo && (S("%s contains an input of type %s with both value and defaultValue props. Input elements must be either controlled or uncontrolled (specify either the value prop, or the defaultValue prop, but not both). Decide between using a controlled or uncontrolled input element and remove one of these props. More info: https://reactjs.org/link/controlled-components", Dr() || "A component", t.type), eo = !0);
      var a = e, i = t.defaultValue == null ? "" : t.defaultValue;
      a._wrapperState = {
        initialChecked: t.checked != null ? t.checked : t.defaultChecked,
        initialValue: wa(t.value != null ? t.value : i),
        controlled: no(t)
      };
    }
    function h(e, t) {
      var a = e, i = t.checked;
      i != null && br(a, "checked", i, !1);
    }
    function C(e, t) {
      var a = e;
      {
        var i = no(t);
        !a._wrapperState.controlled && i && !uu && (S("A component is changing an uncontrolled input to be controlled. This is likely caused by the value changing from undefined to a defined value, which should not happen. Decide between using a controlled or uncontrolled input element for the lifetime of the component. More info: https://reactjs.org/link/controlled-components"), uu = !0), a._wrapperState.controlled && !i && !Cl && (S("A component is changing a controlled input to be uncontrolled. This is likely caused by the value changing from a defined to undefined, which should not happen. Decide between using a controlled or uncontrolled input element for the lifetime of the component. More info: https://reactjs.org/link/controlled-components"), Cl = !0);
      }
      h(e, t);
      var u = wa(t.value), s = t.type;
      if (u != null)
        s === "number" ? (u === 0 && a.value === "" || // We explicitly want to coerce to number here if possible.
        // eslint-disable-next-line
        a.value != u) && (a.value = Or(u)) : a.value !== Or(u) && (a.value = Or(u));
      else if (s === "submit" || s === "reset") {
        a.removeAttribute("value");
        return;
      }
      t.hasOwnProperty("value") ? Ne(a, t.type, u) : t.hasOwnProperty("defaultValue") && Ne(a, t.type, wa(t.defaultValue)), t.checked == null && t.defaultChecked != null && (a.defaultChecked = !!t.defaultChecked);
    }
    function z(e, t, a) {
      var i = e;
      if (t.hasOwnProperty("value") || t.hasOwnProperty("defaultValue")) {
        var u = t.type, s = u === "submit" || u === "reset";
        if (s && (t.value === void 0 || t.value === null))
          return;
        var f = Or(i._wrapperState.initialValue);
        a || f !== i.value && (i.value = f), i.defaultValue = f;
      }
      var p = i.name;
      p !== "" && (i.name = ""), i.defaultChecked = !i.defaultChecked, i.defaultChecked = !!i._wrapperState.initialChecked, p !== "" && (i.name = p);
    }
    function F(e, t) {
      var a = e;
      C(a, t), X(a, t);
    }
    function X(e, t) {
      var a = t.name;
      if (t.type === "radio" && a != null) {
        for (var i = e; i.parentNode; )
          i = i.parentNode;
        Bn(a, "name");
        for (var u = i.querySelectorAll("input[name=" + JSON.stringify("" + a) + '][type="radio"]'), s = 0; s < u.length; s++) {
          var f = u[s];
          if (!(f === e || f.form !== e.form)) {
            var p = Lh(f);
            if (!p)
              throw new Error("ReactDOMInput: Mixing React and non-React radio inputs with the same `name` is not supported.");
            gi(f), C(f, p);
          }
        }
      }
    }
    function Ne(e, t, a) {
      // Focused number inputs synchronize on blur. See ChangeEventPlugin.js
      (t !== "number" || ba(e.ownerDocument) !== e) && (a == null ? e.defaultValue = Or(e._wrapperState.initialValue) : e.defaultValue !== Or(a) && (e.defaultValue = Or(a)));
    }
    var re = !1, Ae = !1, mt = !1;
    function bt(e, t) {
      t.value == null && (typeof t.children == "object" && t.children !== null ? I.Children.forEach(t.children, function(a) {
        a != null && (typeof a == "string" || typeof a == "number" || Ae || (Ae = !0, S("Cannot infer the option value of complex children. Pass a `value` prop or use a plain string as children to <option>.")));
      }) : t.dangerouslySetInnerHTML != null && (mt || (mt = !0, S("Pass a `value` prop if you set dangerouslyInnerHTML so React knows which value should be selected.")))), t.selected != null && !re && (S("Use the `defaultValue` or `value` props on <select> instead of setting `selected` on <option>."), re = !0);
    }
    function rn(e, t) {
      t.value != null && e.setAttribute("value", Or(wa(t.value)));
    }
    var Wt = Array.isArray;
    function st(e) {
      return Wt(e);
    }
    var Gt;
    Gt = !1;
    function hn() {
      var e = Dr();
      return e ? `

Check the render method of \`` + e + "`." : "";
    }
    var Rl = ["value", "defaultValue"];
    function Ko(e) {
      {
        Wo("select", e);
        for (var t = 0; t < Rl.length; t++) {
          var a = Rl[t];
          if (e[a] != null) {
            var i = st(e[a]);
            e.multiple && !i ? S("The `%s` prop supplied to <select> must be an array if `multiple` is true.%s", a, hn()) : !e.multiple && i && S("The `%s` prop supplied to <select> must be a scalar value if `multiple` is false.%s", a, hn());
          }
        }
      }
    }
    function Bi(e, t, a, i) {
      var u = e.options;
      if (t) {
        for (var s = a, f = {}, p = 0; p < s.length; p++)
          f["$" + s[p]] = !0;
        for (var v = 0; v < u.length; v++) {
          var y = f.hasOwnProperty("$" + u[v].value);
          u[v].selected !== y && (u[v].selected = y), y && i && (u[v].defaultSelected = !0);
        }
      } else {
        for (var g = Or(wa(a)), b = null, w = 0; w < u.length; w++) {
          if (u[w].value === g) {
            u[w].selected = !0, i && (u[w].defaultSelected = !0);
            return;
          }
          b === null && !u[w].disabled && (b = u[w]);
        }
        b !== null && (b.selected = !0);
      }
    }
    function qo(e, t) {
      return rt({}, t, {
        value: void 0
      });
    }
    function ou(e, t) {
      var a = e;
      Ko(t), a._wrapperState = {
        wasMultiple: !!t.multiple
      }, t.value !== void 0 && t.defaultValue !== void 0 && !Gt && (S("Select elements must be either controlled or uncontrolled (specify either the value prop, or the defaultValue prop, but not both). Decide between using a controlled or uncontrolled select element and remove one of these props. More info: https://reactjs.org/link/controlled-components"), Gt = !0);
    }
    function Gf(e, t) {
      var a = e;
      a.multiple = !!t.multiple;
      var i = t.value;
      i != null ? Bi(a, !!t.multiple, i, !1) : t.defaultValue != null && Bi(a, !!t.multiple, t.defaultValue, !0);
    }
    function oc(e, t) {
      var a = e, i = a._wrapperState.wasMultiple;
      a._wrapperState.wasMultiple = !!t.multiple;
      var u = t.value;
      u != null ? Bi(a, !!t.multiple, u, !1) : i !== !!t.multiple && (t.defaultValue != null ? Bi(a, !!t.multiple, t.defaultValue, !0) : Bi(a, !!t.multiple, t.multiple ? [] : "", !1));
    }
    function Kf(e, t) {
      var a = e, i = t.value;
      i != null && Bi(a, !!t.multiple, i, !1);
    }
    var ev = !1;
    function qf(e, t) {
      var a = e;
      if (t.dangerouslySetInnerHTML != null)
        throw new Error("`dangerouslySetInnerHTML` does not make sense on <textarea>.");
      var i = rt({}, t, {
        value: void 0,
        defaultValue: void 0,
        children: Or(a._wrapperState.initialValue)
      });
      return i;
    }
    function Xf(e, t) {
      var a = e;
      Wo("textarea", t), t.value !== void 0 && t.defaultValue !== void 0 && !ev && (S("%s contains a textarea with both value and defaultValue props. Textarea elements must be either controlled or uncontrolled (specify either the value prop, or the defaultValue prop, but not both). Decide between using a controlled or uncontrolled textarea and remove one of these props. More info: https://reactjs.org/link/controlled-components", Dr() || "A component"), ev = !0);
      var i = t.value;
      if (i == null) {
        var u = t.children, s = t.defaultValue;
        if (u != null) {
          S("Use the `defaultValue` or `value` props instead of setting children on <textarea>.");
          {
            if (s != null)
              throw new Error("If you supply `defaultValue` on a <textarea>, do not pass children.");
            if (st(u)) {
              if (u.length > 1)
                throw new Error("<textarea> can only have at most one child.");
              u = u[0];
            }
            s = u;
          }
        }
        s == null && (s = ""), i = s;
      }
      a._wrapperState = {
        initialValue: wa(i)
      };
    }
    function tv(e, t) {
      var a = e, i = wa(t.value), u = wa(t.defaultValue);
      if (i != null) {
        var s = Or(i);
        s !== a.value && (a.value = s), t.defaultValue == null && a.defaultValue !== s && (a.defaultValue = s);
      }
      u != null && (a.defaultValue = Or(u));
    }
    function nv(e, t) {
      var a = e, i = a.textContent;
      i === a._wrapperState.initialValue && i !== "" && i !== null && (a.value = i);
    }
    function Wm(e, t) {
      tv(e, t);
    }
    var Ii = "http://www.w3.org/1999/xhtml", Zf = "http://www.w3.org/1998/Math/MathML", Jf = "http://www.w3.org/2000/svg";
    function ed(e) {
      switch (e) {
        case "svg":
          return Jf;
        case "math":
          return Zf;
        default:
          return Ii;
      }
    }
    function td(e, t) {
      return e == null || e === Ii ? ed(t) : e === Jf && t === "foreignObject" ? Ii : e;
    }
    var rv = function(e) {
      return typeof MSApp < "u" && MSApp.execUnsafeLocalFunction ? function(t, a, i, u) {
        MSApp.execUnsafeLocalFunction(function() {
          return e(t, a, i, u);
        });
      } : e;
    }, sc, av = rv(function(e, t) {
      if (e.namespaceURI === Jf && !("innerHTML" in e)) {
        sc = sc || document.createElement("div"), sc.innerHTML = "<svg>" + t.valueOf().toString() + "</svg>";
        for (var a = sc.firstChild; e.firstChild; )
          e.removeChild(e.firstChild);
        for (; a.firstChild; )
          e.appendChild(a.firstChild);
        return;
      }
      e.innerHTML = t;
    }), Qr = 1, Yi = 3, Mn = 8, $i = 9, nd = 11, ao = function(e, t) {
      if (t) {
        var a = e.firstChild;
        if (a && a === e.lastChild && a.nodeType === Yi) {
          a.nodeValue = t;
          return;
        }
      }
      e.textContent = t;
    }, Xo = {
      animation: ["animationDelay", "animationDirection", "animationDuration", "animationFillMode", "animationIterationCount", "animationName", "animationPlayState", "animationTimingFunction"],
      background: ["backgroundAttachment", "backgroundClip", "backgroundColor", "backgroundImage", "backgroundOrigin", "backgroundPositionX", "backgroundPositionY", "backgroundRepeat", "backgroundSize"],
      backgroundPosition: ["backgroundPositionX", "backgroundPositionY"],
      border: ["borderBottomColor", "borderBottomStyle", "borderBottomWidth", "borderImageOutset", "borderImageRepeat", "borderImageSlice", "borderImageSource", "borderImageWidth", "borderLeftColor", "borderLeftStyle", "borderLeftWidth", "borderRightColor", "borderRightStyle", "borderRightWidth", "borderTopColor", "borderTopStyle", "borderTopWidth"],
      borderBlockEnd: ["borderBlockEndColor", "borderBlockEndStyle", "borderBlockEndWidth"],
      borderBlockStart: ["borderBlockStartColor", "borderBlockStartStyle", "borderBlockStartWidth"],
      borderBottom: ["borderBottomColor", "borderBottomStyle", "borderBottomWidth"],
      borderColor: ["borderBottomColor", "borderLeftColor", "borderRightColor", "borderTopColor"],
      borderImage: ["borderImageOutset", "borderImageRepeat", "borderImageSlice", "borderImageSource", "borderImageWidth"],
      borderInlineEnd: ["borderInlineEndColor", "borderInlineEndStyle", "borderInlineEndWidth"],
      borderInlineStart: ["borderInlineStartColor", "borderInlineStartStyle", "borderInlineStartWidth"],
      borderLeft: ["borderLeftColor", "borderLeftStyle", "borderLeftWidth"],
      borderRadius: ["borderBottomLeftRadius", "borderBottomRightRadius", "borderTopLeftRadius", "borderTopRightRadius"],
      borderRight: ["borderRightColor", "borderRightStyle", "borderRightWidth"],
      borderStyle: ["borderBottomStyle", "borderLeftStyle", "borderRightStyle", "borderTopStyle"],
      borderTop: ["borderTopColor", "borderTopStyle", "borderTopWidth"],
      borderWidth: ["borderBottomWidth", "borderLeftWidth", "borderRightWidth", "borderTopWidth"],
      columnRule: ["columnRuleColor", "columnRuleStyle", "columnRuleWidth"],
      columns: ["columnCount", "columnWidth"],
      flex: ["flexBasis", "flexGrow", "flexShrink"],
      flexFlow: ["flexDirection", "flexWrap"],
      font: ["fontFamily", "fontFeatureSettings", "fontKerning", "fontLanguageOverride", "fontSize", "fontSizeAdjust", "fontStretch", "fontStyle", "fontVariant", "fontVariantAlternates", "fontVariantCaps", "fontVariantEastAsian", "fontVariantLigatures", "fontVariantNumeric", "fontVariantPosition", "fontWeight", "lineHeight"],
      fontVariant: ["fontVariantAlternates", "fontVariantCaps", "fontVariantEastAsian", "fontVariantLigatures", "fontVariantNumeric", "fontVariantPosition"],
      gap: ["columnGap", "rowGap"],
      grid: ["gridAutoColumns", "gridAutoFlow", "gridAutoRows", "gridTemplateAreas", "gridTemplateColumns", "gridTemplateRows"],
      gridArea: ["gridColumnEnd", "gridColumnStart", "gridRowEnd", "gridRowStart"],
      gridColumn: ["gridColumnEnd", "gridColumnStart"],
      gridColumnGap: ["columnGap"],
      gridGap: ["columnGap", "rowGap"],
      gridRow: ["gridRowEnd", "gridRowStart"],
      gridRowGap: ["rowGap"],
      gridTemplate: ["gridTemplateAreas", "gridTemplateColumns", "gridTemplateRows"],
      listStyle: ["listStyleImage", "listStylePosition", "listStyleType"],
      margin: ["marginBottom", "marginLeft", "marginRight", "marginTop"],
      marker: ["markerEnd", "markerMid", "markerStart"],
      mask: ["maskClip", "maskComposite", "maskImage", "maskMode", "maskOrigin", "maskPositionX", "maskPositionY", "maskRepeat", "maskSize"],
      maskPosition: ["maskPositionX", "maskPositionY"],
      outline: ["outlineColor", "outlineStyle", "outlineWidth"],
      overflow: ["overflowX", "overflowY"],
      padding: ["paddingBottom", "paddingLeft", "paddingRight", "paddingTop"],
      placeContent: ["alignContent", "justifyContent"],
      placeItems: ["alignItems", "justifyItems"],
      placeSelf: ["alignSelf", "justifySelf"],
      textDecoration: ["textDecorationColor", "textDecorationLine", "textDecorationStyle"],
      textEmphasis: ["textEmphasisColor", "textEmphasisStyle"],
      transition: ["transitionDelay", "transitionDuration", "transitionProperty", "transitionTimingFunction"],
      wordWrap: ["overflowWrap"]
    }, Zo = {
      animationIterationCount: !0,
      aspectRatio: !0,
      borderImageOutset: !0,
      borderImageSlice: !0,
      borderImageWidth: !0,
      boxFlex: !0,
      boxFlexGroup: !0,
      boxOrdinalGroup: !0,
      columnCount: !0,
      columns: !0,
      flex: !0,
      flexGrow: !0,
      flexPositive: !0,
      flexShrink: !0,
      flexNegative: !0,
      flexOrder: !0,
      gridArea: !0,
      gridRow: !0,
      gridRowEnd: !0,
      gridRowSpan: !0,
      gridRowStart: !0,
      gridColumn: !0,
      gridColumnEnd: !0,
      gridColumnSpan: !0,
      gridColumnStart: !0,
      fontWeight: !0,
      lineClamp: !0,
      lineHeight: !0,
      opacity: !0,
      order: !0,
      orphans: !0,
      tabSize: !0,
      widows: !0,
      zIndex: !0,
      zoom: !0,
      // SVG-related properties
      fillOpacity: !0,
      floodOpacity: !0,
      stopOpacity: !0,
      strokeDasharray: !0,
      strokeDashoffset: !0,
      strokeMiterlimit: !0,
      strokeOpacity: !0,
      strokeWidth: !0
    };
    function iv(e, t) {
      return e + t.charAt(0).toUpperCase() + t.substring(1);
    }
    var lv = ["Webkit", "ms", "Moz", "O"];
    Object.keys(Zo).forEach(function(e) {
      lv.forEach(function(t) {
        Zo[iv(t, e)] = Zo[e];
      });
    });
    function cc(e, t, a) {
      var i = t == null || typeof t == "boolean" || t === "";
      return i ? "" : !a && typeof t == "number" && t !== 0 && !(Zo.hasOwnProperty(e) && Zo[e]) ? t + "px" : (oa(t, e), ("" + t).trim());
    }
    var uv = /([A-Z])/g, ov = /^ms-/;
    function io(e) {
      return e.replace(uv, "-$1").toLowerCase().replace(ov, "-ms-");
    }
    var sv = function() {
    };
    {
      var Gm = /^(?:webkit|moz|o)[A-Z]/, Km = /^-ms-/, cv = /-(.)/g, rd = /;\s*$/, Si = {}, su = {}, fv = !1, Jo = !1, qm = function(e) {
        return e.replace(cv, function(t, a) {
          return a.toUpperCase();
        });
      }, dv = function(e) {
        Si.hasOwnProperty(e) && Si[e] || (Si[e] = !0, S(
          "Unsupported style property %s. Did you mean %s?",
          e,
          // As Andi Smith suggests
          // (http://www.andismith.com/blog/2012/02/modernizr-prefixed/), an `-ms` prefix
          // is converted to lowercase `ms`.
          qm(e.replace(Km, "ms-"))
        ));
      }, ad = function(e) {
        Si.hasOwnProperty(e) && Si[e] || (Si[e] = !0, S("Unsupported vendor-prefixed style property %s. Did you mean %s?", e, e.charAt(0).toUpperCase() + e.slice(1)));
      }, id = function(e, t) {
        su.hasOwnProperty(t) && su[t] || (su[t] = !0, S(`Style property values shouldn't contain a semicolon. Try "%s: %s" instead.`, e, t.replace(rd, "")));
      }, pv = function(e, t) {
        fv || (fv = !0, S("`NaN` is an invalid value for the `%s` css style property.", e));
      }, vv = function(e, t) {
        Jo || (Jo = !0, S("`Infinity` is an invalid value for the `%s` css style property.", e));
      };
      sv = function(e, t) {
        e.indexOf("-") > -1 ? dv(e) : Gm.test(e) ? ad(e) : rd.test(t) && id(e, t), typeof t == "number" && (isNaN(t) ? pv(e, t) : isFinite(t) || vv(e, t));
      };
    }
    var hv = sv;
    function Xm(e) {
      {
        var t = "", a = "";
        for (var i in e)
          if (e.hasOwnProperty(i)) {
            var u = e[i];
            if (u != null) {
              var s = i.indexOf("--") === 0;
              t += a + (s ? i : io(i)) + ":", t += cc(i, u, s), a = ";";
            }
          }
        return t || null;
      }
    }
    function mv(e, t) {
      var a = e.style;
      for (var i in t)
        if (t.hasOwnProperty(i)) {
          var u = i.indexOf("--") === 0;
          u || hv(i, t[i]);
          var s = cc(i, t[i], u);
          i === "float" && (i = "cssFloat"), u ? a.setProperty(i, s) : a[i] = s;
        }
    }
    function Zm(e) {
      return e == null || typeof e == "boolean" || e === "";
    }
    function yv(e) {
      var t = {};
      for (var a in e)
        for (var i = Xo[a] || [a], u = 0; u < i.length; u++)
          t[i[u]] = a;
      return t;
    }
    function Jm(e, t) {
      {
        if (!t)
          return;
        var a = yv(e), i = yv(t), u = {};
        for (var s in a) {
          var f = a[s], p = i[s];
          if (p && f !== p) {
            var v = f + "," + p;
            if (u[v])
              continue;
            u[v] = !0, S("%s a style property during rerender (%s) when a conflicting property is set (%s) can lead to styling bugs. To avoid this, don't mix shorthand and non-shorthand properties for the same value; instead, replace the shorthand with separate values.", Zm(e[f]) ? "Removing" : "Updating", f, p);
          }
        }
      }
    }
    var ti = {
      area: !0,
      base: !0,
      br: !0,
      col: !0,
      embed: !0,
      hr: !0,
      img: !0,
      input: !0,
      keygen: !0,
      link: !0,
      meta: !0,
      param: !0,
      source: !0,
      track: !0,
      wbr: !0
      // NOTE: menuitem's close tag should be omitted, but that causes problems.
    }, es = rt({
      menuitem: !0
    }, ti), gv = "__html";
    function fc(e, t) {
      if (t) {
        if (es[e] && (t.children != null || t.dangerouslySetInnerHTML != null))
          throw new Error(e + " is a void element tag and must neither have `children` nor use `dangerouslySetInnerHTML`.");
        if (t.dangerouslySetInnerHTML != null) {
          if (t.children != null)
            throw new Error("Can only set one of `children` or `props.dangerouslySetInnerHTML`.");
          if (typeof t.dangerouslySetInnerHTML != "object" || !(gv in t.dangerouslySetInnerHTML))
            throw new Error("`props.dangerouslySetInnerHTML` must be in the form `{__html: ...}`. Please visit https://reactjs.org/link/dangerously-set-inner-html for more information.");
        }
        if (!t.suppressContentEditableWarning && t.contentEditable && t.children != null && S("A component is `contentEditable` and contains `children` managed by React. It is now your responsibility to guarantee that none of those nodes are unexpectedly modified or duplicated. This is probably not intentional."), t.style != null && typeof t.style != "object")
          throw new Error("The `style` prop expects a mapping from style properties to values, not a string. For example, style={{marginRight: spacing + 'em'}} when using JSX.");
      }
    }
    function Tl(e, t) {
      if (e.indexOf("-") === -1)
        return typeof t.is == "string";
      switch (e) {
        case "annotation-xml":
        case "color-profile":
        case "font-face":
        case "font-face-src":
        case "font-face-uri":
        case "font-face-format":
        case "font-face-name":
        case "missing-glyph":
          return !1;
        default:
          return !0;
      }
    }
    var ts = {
      // HTML
      accept: "accept",
      acceptcharset: "acceptCharset",
      "accept-charset": "acceptCharset",
      accesskey: "accessKey",
      action: "action",
      allowfullscreen: "allowFullScreen",
      alt: "alt",
      as: "as",
      async: "async",
      autocapitalize: "autoCapitalize",
      autocomplete: "autoComplete",
      autocorrect: "autoCorrect",
      autofocus: "autoFocus",
      autoplay: "autoPlay",
      autosave: "autoSave",
      capture: "capture",
      cellpadding: "cellPadding",
      cellspacing: "cellSpacing",
      challenge: "challenge",
      charset: "charSet",
      checked: "checked",
      children: "children",
      cite: "cite",
      class: "className",
      classid: "classID",
      classname: "className",
      cols: "cols",
      colspan: "colSpan",
      content: "content",
      contenteditable: "contentEditable",
      contextmenu: "contextMenu",
      controls: "controls",
      controlslist: "controlsList",
      coords: "coords",
      crossorigin: "crossOrigin",
      dangerouslysetinnerhtml: "dangerouslySetInnerHTML",
      data: "data",
      datetime: "dateTime",
      default: "default",
      defaultchecked: "defaultChecked",
      defaultvalue: "defaultValue",
      defer: "defer",
      dir: "dir",
      disabled: "disabled",
      disablepictureinpicture: "disablePictureInPicture",
      disableremoteplayback: "disableRemotePlayback",
      download: "download",
      draggable: "draggable",
      enctype: "encType",
      enterkeyhint: "enterKeyHint",
      for: "htmlFor",
      form: "form",
      formmethod: "formMethod",
      formaction: "formAction",
      formenctype: "formEncType",
      formnovalidate: "formNoValidate",
      formtarget: "formTarget",
      frameborder: "frameBorder",
      headers: "headers",
      height: "height",
      hidden: "hidden",
      high: "high",
      href: "href",
      hreflang: "hrefLang",
      htmlfor: "htmlFor",
      httpequiv: "httpEquiv",
      "http-equiv": "httpEquiv",
      icon: "icon",
      id: "id",
      imagesizes: "imageSizes",
      imagesrcset: "imageSrcSet",
      innerhtml: "innerHTML",
      inputmode: "inputMode",
      integrity: "integrity",
      is: "is",
      itemid: "itemID",
      itemprop: "itemProp",
      itemref: "itemRef",
      itemscope: "itemScope",
      itemtype: "itemType",
      keyparams: "keyParams",
      keytype: "keyType",
      kind: "kind",
      label: "label",
      lang: "lang",
      list: "list",
      loop: "loop",
      low: "low",
      manifest: "manifest",
      marginwidth: "marginWidth",
      marginheight: "marginHeight",
      max: "max",
      maxlength: "maxLength",
      media: "media",
      mediagroup: "mediaGroup",
      method: "method",
      min: "min",
      minlength: "minLength",
      multiple: "multiple",
      muted: "muted",
      name: "name",
      nomodule: "noModule",
      nonce: "nonce",
      novalidate: "noValidate",
      open: "open",
      optimum: "optimum",
      pattern: "pattern",
      placeholder: "placeholder",
      playsinline: "playsInline",
      poster: "poster",
      preload: "preload",
      profile: "profile",
      radiogroup: "radioGroup",
      readonly: "readOnly",
      referrerpolicy: "referrerPolicy",
      rel: "rel",
      required: "required",
      reversed: "reversed",
      role: "role",
      rows: "rows",
      rowspan: "rowSpan",
      sandbox: "sandbox",
      scope: "scope",
      scoped: "scoped",
      scrolling: "scrolling",
      seamless: "seamless",
      selected: "selected",
      shape: "shape",
      size: "size",
      sizes: "sizes",
      span: "span",
      spellcheck: "spellCheck",
      src: "src",
      srcdoc: "srcDoc",
      srclang: "srcLang",
      srcset: "srcSet",
      start: "start",
      step: "step",
      style: "style",
      summary: "summary",
      tabindex: "tabIndex",
      target: "target",
      title: "title",
      type: "type",
      usemap: "useMap",
      value: "value",
      width: "width",
      wmode: "wmode",
      wrap: "wrap",
      // SVG
      about: "about",
      accentheight: "accentHeight",
      "accent-height": "accentHeight",
      accumulate: "accumulate",
      additive: "additive",
      alignmentbaseline: "alignmentBaseline",
      "alignment-baseline": "alignmentBaseline",
      allowreorder: "allowReorder",
      alphabetic: "alphabetic",
      amplitude: "amplitude",
      arabicform: "arabicForm",
      "arabic-form": "arabicForm",
      ascent: "ascent",
      attributename: "attributeName",
      attributetype: "attributeType",
      autoreverse: "autoReverse",
      azimuth: "azimuth",
      basefrequency: "baseFrequency",
      baselineshift: "baselineShift",
      "baseline-shift": "baselineShift",
      baseprofile: "baseProfile",
      bbox: "bbox",
      begin: "begin",
      bias: "bias",
      by: "by",
      calcmode: "calcMode",
      capheight: "capHeight",
      "cap-height": "capHeight",
      clip: "clip",
      clippath: "clipPath",
      "clip-path": "clipPath",
      clippathunits: "clipPathUnits",
      cliprule: "clipRule",
      "clip-rule": "clipRule",
      color: "color",
      colorinterpolation: "colorInterpolation",
      "color-interpolation": "colorInterpolation",
      colorinterpolationfilters: "colorInterpolationFilters",
      "color-interpolation-filters": "colorInterpolationFilters",
      colorprofile: "colorProfile",
      "color-profile": "colorProfile",
      colorrendering: "colorRendering",
      "color-rendering": "colorRendering",
      contentscripttype: "contentScriptType",
      contentstyletype: "contentStyleType",
      cursor: "cursor",
      cx: "cx",
      cy: "cy",
      d: "d",
      datatype: "datatype",
      decelerate: "decelerate",
      descent: "descent",
      diffuseconstant: "diffuseConstant",
      direction: "direction",
      display: "display",
      divisor: "divisor",
      dominantbaseline: "dominantBaseline",
      "dominant-baseline": "dominantBaseline",
      dur: "dur",
      dx: "dx",
      dy: "dy",
      edgemode: "edgeMode",
      elevation: "elevation",
      enablebackground: "enableBackground",
      "enable-background": "enableBackground",
      end: "end",
      exponent: "exponent",
      externalresourcesrequired: "externalResourcesRequired",
      fill: "fill",
      fillopacity: "fillOpacity",
      "fill-opacity": "fillOpacity",
      fillrule: "fillRule",
      "fill-rule": "fillRule",
      filter: "filter",
      filterres: "filterRes",
      filterunits: "filterUnits",
      floodopacity: "floodOpacity",
      "flood-opacity": "floodOpacity",
      floodcolor: "floodColor",
      "flood-color": "floodColor",
      focusable: "focusable",
      fontfamily: "fontFamily",
      "font-family": "fontFamily",
      fontsize: "fontSize",
      "font-size": "fontSize",
      fontsizeadjust: "fontSizeAdjust",
      "font-size-adjust": "fontSizeAdjust",
      fontstretch: "fontStretch",
      "font-stretch": "fontStretch",
      fontstyle: "fontStyle",
      "font-style": "fontStyle",
      fontvariant: "fontVariant",
      "font-variant": "fontVariant",
      fontweight: "fontWeight",
      "font-weight": "fontWeight",
      format: "format",
      from: "from",
      fx: "fx",
      fy: "fy",
      g1: "g1",
      g2: "g2",
      glyphname: "glyphName",
      "glyph-name": "glyphName",
      glyphorientationhorizontal: "glyphOrientationHorizontal",
      "glyph-orientation-horizontal": "glyphOrientationHorizontal",
      glyphorientationvertical: "glyphOrientationVertical",
      "glyph-orientation-vertical": "glyphOrientationVertical",
      glyphref: "glyphRef",
      gradienttransform: "gradientTransform",
      gradientunits: "gradientUnits",
      hanging: "hanging",
      horizadvx: "horizAdvX",
      "horiz-adv-x": "horizAdvX",
      horizoriginx: "horizOriginX",
      "horiz-origin-x": "horizOriginX",
      ideographic: "ideographic",
      imagerendering: "imageRendering",
      "image-rendering": "imageRendering",
      in2: "in2",
      in: "in",
      inlist: "inlist",
      intercept: "intercept",
      k1: "k1",
      k2: "k2",
      k3: "k3",
      k4: "k4",
      k: "k",
      kernelmatrix: "kernelMatrix",
      kernelunitlength: "kernelUnitLength",
      kerning: "kerning",
      keypoints: "keyPoints",
      keysplines: "keySplines",
      keytimes: "keyTimes",
      lengthadjust: "lengthAdjust",
      letterspacing: "letterSpacing",
      "letter-spacing": "letterSpacing",
      lightingcolor: "lightingColor",
      "lighting-color": "lightingColor",
      limitingconeangle: "limitingConeAngle",
      local: "local",
      markerend: "markerEnd",
      "marker-end": "markerEnd",
      markerheight: "markerHeight",
      markermid: "markerMid",
      "marker-mid": "markerMid",
      markerstart: "markerStart",
      "marker-start": "markerStart",
      markerunits: "markerUnits",
      markerwidth: "markerWidth",
      mask: "mask",
      maskcontentunits: "maskContentUnits",
      maskunits: "maskUnits",
      mathematical: "mathematical",
      mode: "mode",
      numoctaves: "numOctaves",
      offset: "offset",
      opacity: "opacity",
      operator: "operator",
      order: "order",
      orient: "orient",
      orientation: "orientation",
      origin: "origin",
      overflow: "overflow",
      overlineposition: "overlinePosition",
      "overline-position": "overlinePosition",
      overlinethickness: "overlineThickness",
      "overline-thickness": "overlineThickness",
      paintorder: "paintOrder",
      "paint-order": "paintOrder",
      panose1: "panose1",
      "panose-1": "panose1",
      pathlength: "pathLength",
      patterncontentunits: "patternContentUnits",
      patterntransform: "patternTransform",
      patternunits: "patternUnits",
      pointerevents: "pointerEvents",
      "pointer-events": "pointerEvents",
      points: "points",
      pointsatx: "pointsAtX",
      pointsaty: "pointsAtY",
      pointsatz: "pointsAtZ",
      prefix: "prefix",
      preservealpha: "preserveAlpha",
      preserveaspectratio: "preserveAspectRatio",
      primitiveunits: "primitiveUnits",
      property: "property",
      r: "r",
      radius: "radius",
      refx: "refX",
      refy: "refY",
      renderingintent: "renderingIntent",
      "rendering-intent": "renderingIntent",
      repeatcount: "repeatCount",
      repeatdur: "repeatDur",
      requiredextensions: "requiredExtensions",
      requiredfeatures: "requiredFeatures",
      resource: "resource",
      restart: "restart",
      result: "result",
      results: "results",
      rotate: "rotate",
      rx: "rx",
      ry: "ry",
      scale: "scale",
      security: "security",
      seed: "seed",
      shaperendering: "shapeRendering",
      "shape-rendering": "shapeRendering",
      slope: "slope",
      spacing: "spacing",
      specularconstant: "specularConstant",
      specularexponent: "specularExponent",
      speed: "speed",
      spreadmethod: "spreadMethod",
      startoffset: "startOffset",
      stddeviation: "stdDeviation",
      stemh: "stemh",
      stemv: "stemv",
      stitchtiles: "stitchTiles",
      stopcolor: "stopColor",
      "stop-color": "stopColor",
      stopopacity: "stopOpacity",
      "stop-opacity": "stopOpacity",
      strikethroughposition: "strikethroughPosition",
      "strikethrough-position": "strikethroughPosition",
      strikethroughthickness: "strikethroughThickness",
      "strikethrough-thickness": "strikethroughThickness",
      string: "string",
      stroke: "stroke",
      strokedasharray: "strokeDasharray",
      "stroke-dasharray": "strokeDasharray",
      strokedashoffset: "strokeDashoffset",
      "stroke-dashoffset": "strokeDashoffset",
      strokelinecap: "strokeLinecap",
      "stroke-linecap": "strokeLinecap",
      strokelinejoin: "strokeLinejoin",
      "stroke-linejoin": "strokeLinejoin",
      strokemiterlimit: "strokeMiterlimit",
      "stroke-miterlimit": "strokeMiterlimit",
      strokewidth: "strokeWidth",
      "stroke-width": "strokeWidth",
      strokeopacity: "strokeOpacity",
      "stroke-opacity": "strokeOpacity",
      suppresscontenteditablewarning: "suppressContentEditableWarning",
      suppresshydrationwarning: "suppressHydrationWarning",
      surfacescale: "surfaceScale",
      systemlanguage: "systemLanguage",
      tablevalues: "tableValues",
      targetx: "targetX",
      targety: "targetY",
      textanchor: "textAnchor",
      "text-anchor": "textAnchor",
      textdecoration: "textDecoration",
      "text-decoration": "textDecoration",
      textlength: "textLength",
      textrendering: "textRendering",
      "text-rendering": "textRendering",
      to: "to",
      transform: "transform",
      typeof: "typeof",
      u1: "u1",
      u2: "u2",
      underlineposition: "underlinePosition",
      "underline-position": "underlinePosition",
      underlinethickness: "underlineThickness",
      "underline-thickness": "underlineThickness",
      unicode: "unicode",
      unicodebidi: "unicodeBidi",
      "unicode-bidi": "unicodeBidi",
      unicoderange: "unicodeRange",
      "unicode-range": "unicodeRange",
      unitsperem: "unitsPerEm",
      "units-per-em": "unitsPerEm",
      unselectable: "unselectable",
      valphabetic: "vAlphabetic",
      "v-alphabetic": "vAlphabetic",
      values: "values",
      vectoreffect: "vectorEffect",
      "vector-effect": "vectorEffect",
      version: "version",
      vertadvy: "vertAdvY",
      "vert-adv-y": "vertAdvY",
      vertoriginx: "vertOriginX",
      "vert-origin-x": "vertOriginX",
      vertoriginy: "vertOriginY",
      "vert-origin-y": "vertOriginY",
      vhanging: "vHanging",
      "v-hanging": "vHanging",
      videographic: "vIdeographic",
      "v-ideographic": "vIdeographic",
      viewbox: "viewBox",
      viewtarget: "viewTarget",
      visibility: "visibility",
      vmathematical: "vMathematical",
      "v-mathematical": "vMathematical",
      vocab: "vocab",
      widths: "widths",
      wordspacing: "wordSpacing",
      "word-spacing": "wordSpacing",
      writingmode: "writingMode",
      "writing-mode": "writingMode",
      x1: "x1",
      x2: "x2",
      x: "x",
      xchannelselector: "xChannelSelector",
      xheight: "xHeight",
      "x-height": "xHeight",
      xlinkactuate: "xlinkActuate",
      "xlink:actuate": "xlinkActuate",
      xlinkarcrole: "xlinkArcrole",
      "xlink:arcrole": "xlinkArcrole",
      xlinkhref: "xlinkHref",
      "xlink:href": "xlinkHref",
      xlinkrole: "xlinkRole",
      "xlink:role": "xlinkRole",
      xlinkshow: "xlinkShow",
      "xlink:show": "xlinkShow",
      xlinktitle: "xlinkTitle",
      "xlink:title": "xlinkTitle",
      xlinktype: "xlinkType",
      "xlink:type": "xlinkType",
      xmlbase: "xmlBase",
      "xml:base": "xmlBase",
      xmllang: "xmlLang",
      "xml:lang": "xmlLang",
      xmlns: "xmlns",
      "xml:space": "xmlSpace",
      xmlnsxlink: "xmlnsXlink",
      "xmlns:xlink": "xmlnsXlink",
      xmlspace: "xmlSpace",
      y1: "y1",
      y2: "y2",
      y: "y",
      ychannelselector: "yChannelSelector",
      z: "z",
      zoomandpan: "zoomAndPan"
    }, dc = {
      "aria-current": 0,
      // state
      "aria-description": 0,
      "aria-details": 0,
      "aria-disabled": 0,
      // state
      "aria-hidden": 0,
      // state
      "aria-invalid": 0,
      // state
      "aria-keyshortcuts": 0,
      "aria-label": 0,
      "aria-roledescription": 0,
      // Widget Attributes
      "aria-autocomplete": 0,
      "aria-checked": 0,
      "aria-expanded": 0,
      "aria-haspopup": 0,
      "aria-level": 0,
      "aria-modal": 0,
      "aria-multiline": 0,
      "aria-multiselectable": 0,
      "aria-orientation": 0,
      "aria-placeholder": 0,
      "aria-pressed": 0,
      "aria-readonly": 0,
      "aria-required": 0,
      "aria-selected": 0,
      "aria-sort": 0,
      "aria-valuemax": 0,
      "aria-valuemin": 0,
      "aria-valuenow": 0,
      "aria-valuetext": 0,
      // Live Region Attributes
      "aria-atomic": 0,
      "aria-busy": 0,
      "aria-live": 0,
      "aria-relevant": 0,
      // Drag-and-Drop Attributes
      "aria-dropeffect": 0,
      "aria-grabbed": 0,
      // Relationship Attributes
      "aria-activedescendant": 0,
      "aria-colcount": 0,
      "aria-colindex": 0,
      "aria-colspan": 0,
      "aria-controls": 0,
      "aria-describedby": 0,
      "aria-errormessage": 0,
      "aria-flowto": 0,
      "aria-labelledby": 0,
      "aria-owns": 0,
      "aria-posinset": 0,
      "aria-rowcount": 0,
      "aria-rowindex": 0,
      "aria-rowspan": 0,
      "aria-setsize": 0
    }, lo = {}, ey = new RegExp("^(aria)-[" + ee + "]*$"), uo = new RegExp("^(aria)[A-Z][" + ee + "]*$");
    function ld(e, t) {
      {
        if (xr.call(lo, t) && lo[t])
          return !0;
        if (uo.test(t)) {
          var a = "aria-" + t.slice(4).toLowerCase(), i = dc.hasOwnProperty(a) ? a : null;
          if (i == null)
            return S("Invalid ARIA attribute `%s`. ARIA attributes follow the pattern aria-* and must be lowercase.", t), lo[t] = !0, !0;
          if (t !== i)
            return S("Invalid ARIA attribute `%s`. Did you mean `%s`?", t, i), lo[t] = !0, !0;
        }
        if (ey.test(t)) {
          var u = t.toLowerCase(), s = dc.hasOwnProperty(u) ? u : null;
          if (s == null)
            return lo[t] = !0, !1;
          if (t !== s)
            return S("Unknown ARIA attribute `%s`. Did you mean `%s`?", t, s), lo[t] = !0, !0;
        }
      }
      return !0;
    }
    function ns(e, t) {
      {
        var a = [];
        for (var i in t) {
          var u = ld(e, i);
          u || a.push(i);
        }
        var s = a.map(function(f) {
          return "`" + f + "`";
        }).join(", ");
        a.length === 1 ? S("Invalid aria prop %s on <%s> tag. For details, see https://reactjs.org/link/invalid-aria-props", s, e) : a.length > 1 && S("Invalid aria props %s on <%s> tag. For details, see https://reactjs.org/link/invalid-aria-props", s, e);
      }
    }
    function ud(e, t) {
      Tl(e, t) || ns(e, t);
    }
    var od = !1;
    function pc(e, t) {
      {
        if (e !== "input" && e !== "textarea" && e !== "select")
          return;
        t != null && t.value === null && !od && (od = !0, e === "select" && t.multiple ? S("`value` prop on `%s` should not be null. Consider using an empty array when `multiple` is set to `true` to clear the component or `undefined` for uncontrolled components.", e) : S("`value` prop on `%s` should not be null. Consider using an empty string to clear the component or `undefined` for uncontrolled components.", e));
      }
    }
    var cu = function() {
    };
    {
      var lr = {}, sd = /^on./, vc = /^on[^A-Z]/, Sv = new RegExp("^(aria)-[" + ee + "]*$"), Ev = new RegExp("^(aria)[A-Z][" + ee + "]*$");
      cu = function(e, t, a, i) {
        if (xr.call(lr, t) && lr[t])
          return !0;
        var u = t.toLowerCase();
        if (u === "onfocusin" || u === "onfocusout")
          return S("React uses onFocus and onBlur instead of onFocusIn and onFocusOut. All React events are normalized to bubble, so onFocusIn and onFocusOut are not needed/supported by React."), lr[t] = !0, !0;
        if (i != null) {
          var s = i.registrationNameDependencies, f = i.possibleRegistrationNames;
          if (s.hasOwnProperty(t))
            return !0;
          var p = f.hasOwnProperty(u) ? f[u] : null;
          if (p != null)
            return S("Invalid event handler property `%s`. Did you mean `%s`?", t, p), lr[t] = !0, !0;
          if (sd.test(t))
            return S("Unknown event handler property `%s`. It will be ignored.", t), lr[t] = !0, !0;
        } else if (sd.test(t))
          return vc.test(t) && S("Invalid event handler property `%s`. React events use the camelCase naming convention, for example `onClick`.", t), lr[t] = !0, !0;
        if (Sv.test(t) || Ev.test(t))
          return !0;
        if (u === "innerhtml")
          return S("Directly setting property `innerHTML` is not permitted. For more information, lookup documentation on `dangerouslySetInnerHTML`."), lr[t] = !0, !0;
        if (u === "aria")
          return S("The `aria` attribute is reserved for future use in React. Pass individual `aria-` attributes instead."), lr[t] = !0, !0;
        if (u === "is" && a !== null && a !== void 0 && typeof a != "string")
          return S("Received a `%s` for a string attribute `is`. If this is expected, cast the value to a string.", typeof a), lr[t] = !0, !0;
        if (typeof a == "number" && isNaN(a))
          return S("Received NaN for the `%s` attribute. If this is expected, cast the value to a string.", t), lr[t] = !0, !0;
        var v = tn(t), y = v !== null && v.type === In;
        if (ts.hasOwnProperty(u)) {
          var g = ts[u];
          if (g !== t)
            return S("Invalid DOM property `%s`. Did you mean `%s`?", t, g), lr[t] = !0, !0;
        } else if (!y && t !== u)
          return S("React does not recognize the `%s` prop on a DOM element. If you intentionally want it to appear in the DOM as a custom attribute, spell it as lowercase `%s` instead. If you accidentally passed it from a parent component, remove it from the DOM element.", t, u), lr[t] = !0, !0;
        return typeof a == "boolean" && on(t, a, v, !1) ? (a ? S('Received `%s` for a non-boolean attribute `%s`.\n\nIf you want to write it to the DOM, pass a string instead: %s="%s" or %s={value.toString()}.', a, t, t, a, t) : S('Received `%s` for a non-boolean attribute `%s`.\n\nIf you want to write it to the DOM, pass a string instead: %s="%s" or %s={value.toString()}.\n\nIf you used to conditionally omit it with %s={condition && value}, pass %s={condition ? value : undefined} instead.', a, t, t, a, t, t, t), lr[t] = !0, !0) : y ? !0 : on(t, a, v, !1) ? (lr[t] = !0, !1) : ((a === "false" || a === "true") && v !== null && v.type === Ln && (S("Received the string `%s` for the boolean attribute `%s`. %s Did you mean %s={%s}?", a, t, a === "false" ? "The browser will interpret it as a truthy value." : 'Although this works, it will not work as expected if you pass the string "false".', t, a), lr[t] = !0), !0);
      };
    }
    var Cv = function(e, t, a) {
      {
        var i = [];
        for (var u in t) {
          var s = cu(e, u, t[u], a);
          s || i.push(u);
        }
        var f = i.map(function(p) {
          return "`" + p + "`";
        }).join(", ");
        i.length === 1 ? S("Invalid value for prop %s on <%s> tag. Either remove it from the element, or pass a string or number value to keep it in the DOM. For details, see https://reactjs.org/link/attribute-behavior ", f, e) : i.length > 1 && S("Invalid values for props %s on <%s> tag. Either remove them from the element, or pass a string or number value to keep them in the DOM. For details, see https://reactjs.org/link/attribute-behavior ", f, e);
      }
    };
    function Rv(e, t, a) {
      Tl(e, t) || Cv(e, t, a);
    }
    var cd = 1, hc = 2, _a = 4, fd = cd | hc | _a, fu = null;
    function ty(e) {
      fu !== null && S("Expected currently replaying event to be null. This error is likely caused by a bug in React. Please file an issue."), fu = e;
    }
    function ny() {
      fu === null && S("Expected currently replaying event to not be null. This error is likely caused by a bug in React. Please file an issue."), fu = null;
    }
    function rs(e) {
      return e === fu;
    }
    function dd(e) {
      var t = e.target || e.srcElement || window;
      return t.correspondingUseElement && (t = t.correspondingUseElement), t.nodeType === Yi ? t.parentNode : t;
    }
    var mc = null, du = null, Vt = null;
    function yc(e) {
      var t = Do(e);
      if (t) {
        if (typeof mc != "function")
          throw new Error("setRestoreImplementation() needs to be called to handle a target for controlled events. This error is likely caused by a bug in React. Please file an issue.");
        var a = t.stateNode;
        if (a) {
          var i = Lh(a);
          mc(t.stateNode, t.type, i);
        }
      }
    }
    function gc(e) {
      mc = e;
    }
    function oo(e) {
      du ? Vt ? Vt.push(e) : Vt = [e] : du = e;
    }
    function Tv() {
      return du !== null || Vt !== null;
    }
    function Sc() {
      if (du) {
        var e = du, t = Vt;
        if (du = null, Vt = null, yc(e), t)
          for (var a = 0; a < t.length; a++)
            yc(t[a]);
      }
    }
    var so = function(e, t) {
      return e(t);
    }, as = function() {
    }, wl = !1;
    function wv() {
      var e = Tv();
      e && (as(), Sc());
    }
    function xv(e, t, a) {
      if (wl)
        return e(t, a);
      wl = !0;
      try {
        return so(e, t, a);
      } finally {
        wl = !1, wv();
      }
    }
    function ry(e, t, a) {
      so = e, as = a;
    }
    function bv(e) {
      return e === "button" || e === "input" || e === "select" || e === "textarea";
    }
    function Ec(e, t, a) {
      switch (e) {
        case "onClick":
        case "onClickCapture":
        case "onDoubleClick":
        case "onDoubleClickCapture":
        case "onMouseDown":
        case "onMouseDownCapture":
        case "onMouseMove":
        case "onMouseMoveCapture":
        case "onMouseUp":
        case "onMouseUpCapture":
        case "onMouseEnter":
          return !!(a.disabled && bv(t));
        default:
          return !1;
      }
    }
    function xl(e, t) {
      var a = e.stateNode;
      if (a === null)
        return null;
      var i = Lh(a);
      if (i === null)
        return null;
      var u = i[t];
      if (Ec(t, e.type, i))
        return null;
      if (u && typeof u != "function")
        throw new Error("Expected `" + t + "` listener to be a function, instead got a value of `" + typeof u + "` type.");
      return u;
    }
    var is = !1;
    if (On)
      try {
        var pu = {};
        Object.defineProperty(pu, "passive", {
          get: function() {
            is = !0;
          }
        }), window.addEventListener("test", pu, pu), window.removeEventListener("test", pu, pu);
      } catch {
        is = !1;
      }
    function Cc(e, t, a, i, u, s, f, p, v) {
      var y = Array.prototype.slice.call(arguments, 3);
      try {
        t.apply(a, y);
      } catch (g) {
        this.onError(g);
      }
    }
    var Rc = Cc;
    if (typeof window < "u" && typeof window.dispatchEvent == "function" && typeof document < "u" && typeof document.createEvent == "function") {
      var pd = document.createElement("react");
      Rc = function(t, a, i, u, s, f, p, v, y) {
        if (typeof document > "u" || document === null)
          throw new Error("The `document` global was defined when React was initialized, but is not defined anymore. This can happen in a test environment if a component schedules an update from an asynchronous callback, but the test has already finished running. To solve this, you can either unmount the component at the end of your test (and ensure that any asynchronous operations get canceled in `componentWillUnmount`), or you can change the test itself to be asynchronous.");
        var g = document.createEvent("Event"), b = !1, w = !0, N = window.event, A = Object.getOwnPropertyDescriptor(window, "event");
        function H() {
          pd.removeEventListener(P, ze, !1), typeof window.event < "u" && window.hasOwnProperty("event") && (window.event = N);
        }
        var ue = Array.prototype.slice.call(arguments, 3);
        function ze() {
          b = !0, H(), a.apply(i, ue), w = !1;
        }
        var be, wt = !1, yt = !1;
        function O(L) {
          if (be = L.error, wt = !0, be === null && L.colno === 0 && L.lineno === 0 && (yt = !0), L.defaultPrevented && be != null && typeof be == "object")
            try {
              be._suppressLogging = !0;
            } catch {
            }
        }
        var P = "react-" + (t || "invokeguardedcallback");
        if (window.addEventListener("error", O), pd.addEventListener(P, ze, !1), g.initEvent(P, !1, !1), pd.dispatchEvent(g), A && Object.defineProperty(window, "event", A), b && w && (wt ? yt && (be = new Error("A cross-origin error was thrown. React doesn't have access to the actual error object in development. See https://reactjs.org/link/crossorigin-error for more information.")) : be = new Error(`An error was thrown inside one of your components, but React doesn't know what it was. This is likely due to browser flakiness. React does its best to preserve the "Pause on exceptions" behavior of the DevTools, which requires some DEV-mode only tricks. It's possible that these don't work in your browser. Try triggering the error in production mode, or switching to a modern browser. If you suspect that this is actually an issue with React, please file an issue.`), this.onError(be)), window.removeEventListener("error", O), !b)
          return H(), Cc.apply(this, arguments);
      };
    }
    var _v = Rc, co = !1, Tc = null, fo = !1, Ei = null, kv = {
      onError: function(e) {
        co = !0, Tc = e;
      }
    };
    function bl(e, t, a, i, u, s, f, p, v) {
      co = !1, Tc = null, _v.apply(kv, arguments);
    }
    function Ci(e, t, a, i, u, s, f, p, v) {
      if (bl.apply(this, arguments), co) {
        var y = us();
        fo || (fo = !0, Ei = y);
      }
    }
    function ls() {
      if (fo) {
        var e = Ei;
        throw fo = !1, Ei = null, e;
      }
    }
    function Qi() {
      return co;
    }
    function us() {
      if (co) {
        var e = Tc;
        return co = !1, Tc = null, e;
      } else
        throw new Error("clearCaughtError was called but no error was captured. This error is likely caused by a bug in React. Please file an issue.");
    }
    function po(e) {
      return e._reactInternals;
    }
    function ay(e) {
      return e._reactInternals !== void 0;
    }
    function vu(e, t) {
      e._reactInternals = t;
    }
    var De = (
      /*                      */
      0
    ), ni = (
      /*                */
      1
    ), mn = (
      /*                    */
      2
    ), Ct = (
      /*                       */
      4
    ), ka = (
      /*                */
      16
    ), Da = (
      /*                 */
      32
    ), an = (
      /*                     */
      64
    ), _e = (
      /*                   */
      128
    ), Cr = (
      /*            */
      256
    ), En = (
      /*                          */
      512
    ), $n = (
      /*                     */
      1024
    ), Wr = (
      /*                      */
      2048
    ), Gr = (
      /*                    */
      4096
    ), Nn = (
      /*                   */
      8192
    ), vo = (
      /*             */
      16384
    ), Dv = (
      /*               */
      32767
    ), os = (
      /*                   */
      32768
    ), Xn = (
      /*                */
      65536
    ), wc = (
      /* */
      131072
    ), Ri = (
      /*                       */
      1048576
    ), ho = (
      /*                    */
      2097152
    ), Wi = (
      /*                 */
      4194304
    ), xc = (
      /*                */
      8388608
    ), _l = (
      /*               */
      16777216
    ), Ti = (
      /*              */
      33554432
    ), kl = (
      // TODO: Remove Update flag from before mutation phase by re-landing Visibility
      // flag logic (see #20043)
      Ct | $n | 0
    ), Dl = mn | Ct | ka | Da | En | Gr | Nn, Ol = Ct | an | En | Nn, Gi = Wr | ka, zn = Wi | xc | ho, Oa = k.ReactCurrentOwner;
    function da(e) {
      var t = e, a = e;
      if (e.alternate)
        for (; t.return; )
          t = t.return;
      else {
        var i = t;
        do
          t = i, (t.flags & (mn | Gr)) !== De && (a = t.return), i = t.return;
        while (i);
      }
      return t.tag === J ? a : null;
    }
    function wi(e) {
      if (e.tag === ke) {
        var t = e.memoizedState;
        if (t === null) {
          var a = e.alternate;
          a !== null && (t = a.memoizedState);
        }
        if (t !== null)
          return t.dehydrated;
      }
      return null;
    }
    function xi(e) {
      return e.tag === J ? e.stateNode.containerInfo : null;
    }
    function hu(e) {
      return da(e) === e;
    }
    function Ov(e) {
      {
        var t = Oa.current;
        if (t !== null && t.tag === ce) {
          var a = t, i = a.stateNode;
          i._warnedAboutRefsInRender || S("%s is accessing isMounted inside its render() function. render() should be a pure function of props and state. It should never access something that requires stale data from the previous render, such as refs. Move this logic to componentDidMount and componentDidUpdate instead.", We(a) || "A component"), i._warnedAboutRefsInRender = !0;
        }
      }
      var u = po(e);
      return u ? da(u) === u : !1;
    }
    function bc(e) {
      if (da(e) !== e)
        throw new Error("Unable to find node on an unmounted component.");
    }
    function _c(e) {
      var t = e.alternate;
      if (!t) {
        var a = da(e);
        if (a === null)
          throw new Error("Unable to find node on an unmounted component.");
        return a !== e ? null : e;
      }
      for (var i = e, u = t; ; ) {
        var s = i.return;
        if (s === null)
          break;
        var f = s.alternate;
        if (f === null) {
          var p = s.return;
          if (p !== null) {
            i = u = p;
            continue;
          }
          break;
        }
        if (s.child === f.child) {
          for (var v = s.child; v; ) {
            if (v === i)
              return bc(s), e;
            if (v === u)
              return bc(s), t;
            v = v.sibling;
          }
          throw new Error("Unable to find node on an unmounted component.");
        }
        if (i.return !== u.return)
          i = s, u = f;
        else {
          for (var y = !1, g = s.child; g; ) {
            if (g === i) {
              y = !0, i = s, u = f;
              break;
            }
            if (g === u) {
              y = !0, u = s, i = f;
              break;
            }
            g = g.sibling;
          }
          if (!y) {
            for (g = f.child; g; ) {
              if (g === i) {
                y = !0, i = f, u = s;
                break;
              }
              if (g === u) {
                y = !0, u = f, i = s;
                break;
              }
              g = g.sibling;
            }
            if (!y)
              throw new Error("Child was not found in either parent set. This indicates a bug in React related to the return pointer. Please file an issue.");
          }
        }
        if (i.alternate !== u)
          throw new Error("Return fibers should always be each others' alternates. This error is likely caused by a bug in React. Please file an issue.");
      }
      if (i.tag !== J)
        throw new Error("Unable to find node on an unmounted component.");
      return i.stateNode.current === i ? e : t;
    }
    function Kr(e) {
      var t = _c(e);
      return t !== null ? qr(t) : null;
    }
    function qr(e) {
      if (e.tag === ae || e.tag === Ve)
        return e;
      for (var t = e.child; t !== null; ) {
        var a = qr(t);
        if (a !== null)
          return a;
        t = t.sibling;
      }
      return null;
    }
    function dn(e) {
      var t = _c(e);
      return t !== null ? La(t) : null;
    }
    function La(e) {
      if (e.tag === ae || e.tag === Ve)
        return e;
      for (var t = e.child; t !== null; ) {
        if (t.tag !== Se) {
          var a = La(t);
          if (a !== null)
            return a;
        }
        t = t.sibling;
      }
      return null;
    }
    var vd = j.unstable_scheduleCallback, Lv = j.unstable_cancelCallback, hd = j.unstable_shouldYield, md = j.unstable_requestPaint, Qn = j.unstable_now, kc = j.unstable_getCurrentPriorityLevel, ss = j.unstable_ImmediatePriority, Ll = j.unstable_UserBlockingPriority, Ki = j.unstable_NormalPriority, iy = j.unstable_LowPriority, mu = j.unstable_IdlePriority, Dc = j.unstable_yieldValue, Mv = j.unstable_setDisableYieldValue, yu = null, wn = null, le = null, pa = !1, Xr = typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u";
    function mo(e) {
      if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ > "u")
        return !1;
      var t = __REACT_DEVTOOLS_GLOBAL_HOOK__;
      if (t.isDisabled)
        return !0;
      if (!t.supportsFiber)
        return S("The installed version of React DevTools is too old and will not work with the current version of React. Please update React DevTools. https://reactjs.org/link/react-devtools"), !0;
      try {
        Ie && (e = rt({}, e, {
          getLaneLabelMap: gu,
          injectProfilingHooks: Ma
        })), yu = t.inject(e), wn = t;
      } catch (a) {
        S("React instrumentation encountered an error: %s.", a);
      }
      return !!t.checkDCE;
    }
    function yd(e, t) {
      if (wn && typeof wn.onScheduleFiberRoot == "function")
        try {
          wn.onScheduleFiberRoot(yu, e, t);
        } catch (a) {
          pa || (pa = !0, S("React instrumentation encountered an error: %s", a));
        }
    }
    function gd(e, t) {
      if (wn && typeof wn.onCommitFiberRoot == "function")
        try {
          var a = (e.current.flags & _e) === _e;
          if (Pe) {
            var i;
            switch (t) {
              case Lr:
                i = ss;
                break;
              case _i:
                i = Ll;
                break;
              case Na:
                i = Ki;
                break;
              case za:
                i = mu;
                break;
              default:
                i = Ki;
                break;
            }
            wn.onCommitFiberRoot(yu, e, i, a);
          }
        } catch (u) {
          pa || (pa = !0, S("React instrumentation encountered an error: %s", u));
        }
    }
    function Sd(e) {
      if (wn && typeof wn.onPostCommitFiberRoot == "function")
        try {
          wn.onPostCommitFiberRoot(yu, e);
        } catch (t) {
          pa || (pa = !0, S("React instrumentation encountered an error: %s", t));
        }
    }
    function Ed(e) {
      if (wn && typeof wn.onCommitFiberUnmount == "function")
        try {
          wn.onCommitFiberUnmount(yu, e);
        } catch (t) {
          pa || (pa = !0, S("React instrumentation encountered an error: %s", t));
        }
    }
    function yn(e) {
      if (typeof Dc == "function" && (Mv(e), Fe(e)), wn && typeof wn.setStrictMode == "function")
        try {
          wn.setStrictMode(yu, e);
        } catch (t) {
          pa || (pa = !0, S("React instrumentation encountered an error: %s", t));
        }
    }
    function Ma(e) {
      le = e;
    }
    function gu() {
      {
        for (var e = /* @__PURE__ */ new Map(), t = 1, a = 0; a < Cu; a++) {
          var i = Av(t);
          e.set(t, i), t *= 2;
        }
        return e;
      }
    }
    function Cd(e) {
      le !== null && typeof le.markCommitStarted == "function" && le.markCommitStarted(e);
    }
    function Rd() {
      le !== null && typeof le.markCommitStopped == "function" && le.markCommitStopped();
    }
    function va(e) {
      le !== null && typeof le.markComponentRenderStarted == "function" && le.markComponentRenderStarted(e);
    }
    function ha() {
      le !== null && typeof le.markComponentRenderStopped == "function" && le.markComponentRenderStopped();
    }
    function Td(e) {
      le !== null && typeof le.markComponentPassiveEffectMountStarted == "function" && le.markComponentPassiveEffectMountStarted(e);
    }
    function Nv() {
      le !== null && typeof le.markComponentPassiveEffectMountStopped == "function" && le.markComponentPassiveEffectMountStopped();
    }
    function qi(e) {
      le !== null && typeof le.markComponentPassiveEffectUnmountStarted == "function" && le.markComponentPassiveEffectUnmountStarted(e);
    }
    function Ml() {
      le !== null && typeof le.markComponentPassiveEffectUnmountStopped == "function" && le.markComponentPassiveEffectUnmountStopped();
    }
    function Oc(e) {
      le !== null && typeof le.markComponentLayoutEffectMountStarted == "function" && le.markComponentLayoutEffectMountStarted(e);
    }
    function zv() {
      le !== null && typeof le.markComponentLayoutEffectMountStopped == "function" && le.markComponentLayoutEffectMountStopped();
    }
    function cs(e) {
      le !== null && typeof le.markComponentLayoutEffectUnmountStarted == "function" && le.markComponentLayoutEffectUnmountStarted(e);
    }
    function wd() {
      le !== null && typeof le.markComponentLayoutEffectUnmountStopped == "function" && le.markComponentLayoutEffectUnmountStopped();
    }
    function fs(e, t, a) {
      le !== null && typeof le.markComponentErrored == "function" && le.markComponentErrored(e, t, a);
    }
    function bi(e, t, a) {
      le !== null && typeof le.markComponentSuspended == "function" && le.markComponentSuspended(e, t, a);
    }
    function ds(e) {
      le !== null && typeof le.markLayoutEffectsStarted == "function" && le.markLayoutEffectsStarted(e);
    }
    function ps() {
      le !== null && typeof le.markLayoutEffectsStopped == "function" && le.markLayoutEffectsStopped();
    }
    function Su(e) {
      le !== null && typeof le.markPassiveEffectsStarted == "function" && le.markPassiveEffectsStarted(e);
    }
    function xd() {
      le !== null && typeof le.markPassiveEffectsStopped == "function" && le.markPassiveEffectsStopped();
    }
    function Eu(e) {
      le !== null && typeof le.markRenderStarted == "function" && le.markRenderStarted(e);
    }
    function Uv() {
      le !== null && typeof le.markRenderYielded == "function" && le.markRenderYielded();
    }
    function Lc() {
      le !== null && typeof le.markRenderStopped == "function" && le.markRenderStopped();
    }
    function gn(e) {
      le !== null && typeof le.markRenderScheduled == "function" && le.markRenderScheduled(e);
    }
    function Mc(e, t) {
      le !== null && typeof le.markForceUpdateScheduled == "function" && le.markForceUpdateScheduled(e, t);
    }
    function vs(e, t) {
      le !== null && typeof le.markStateUpdateScheduled == "function" && le.markStateUpdateScheduled(e, t);
    }
    var Oe = (
      /*                         */
      0
    ), vt = (
      /*                 */
      1
    ), Mt = (
      /*                    */
      2
    ), Kt = (
      /*               */
      8
    ), Nt = (
      /*              */
      16
    ), Un = Math.clz32 ? Math.clz32 : hs, Zn = Math.log, Nc = Math.LN2;
    function hs(e) {
      var t = e >>> 0;
      return t === 0 ? 32 : 31 - (Zn(t) / Nc | 0) | 0;
    }
    var Cu = 31, $ = (
      /*                        */
      0
    ), Dt = (
      /*                          */
      0
    ), Be = (
      /*                        */
      1
    ), Nl = (
      /*    */
      2
    ), ri = (
      /*             */
      4
    ), Rr = (
      /*            */
      8
    ), xn = (
      /*                     */
      16
    ), Xi = (
      /*                */
      32
    ), zl = (
      /*                       */
      4194240
    ), Ru = (
      /*                        */
      64
    ), zc = (
      /*                        */
      128
    ), Uc = (
      /*                        */
      256
    ), Ac = (
      /*                        */
      512
    ), jc = (
      /*                        */
      1024
    ), Fc = (
      /*                        */
      2048
    ), Hc = (
      /*                        */
      4096
    ), Pc = (
      /*                        */
      8192
    ), Vc = (
      /*                        */
      16384
    ), Tu = (
      /*                       */
      32768
    ), Bc = (
      /*                       */
      65536
    ), yo = (
      /*                       */
      131072
    ), go = (
      /*                       */
      262144
    ), Ic = (
      /*                       */
      524288
    ), ms = (
      /*                       */
      1048576
    ), Yc = (
      /*                       */
      2097152
    ), ys = (
      /*                            */
      130023424
    ), wu = (
      /*                             */
      4194304
    ), $c = (
      /*                             */
      8388608
    ), gs = (
      /*                             */
      16777216
    ), Qc = (
      /*                             */
      33554432
    ), Wc = (
      /*                             */
      67108864
    ), bd = wu, Ss = (
      /*          */
      134217728
    ), _d = (
      /*                          */
      268435455
    ), Es = (
      /*               */
      268435456
    ), xu = (
      /*                        */
      536870912
    ), Zr = (
      /*                   */
      1073741824
    );
    function Av(e) {
      {
        if (e & Be)
          return "Sync";
        if (e & Nl)
          return "InputContinuousHydration";
        if (e & ri)
          return "InputContinuous";
        if (e & Rr)
          return "DefaultHydration";
        if (e & xn)
          return "Default";
        if (e & Xi)
          return "TransitionHydration";
        if (e & zl)
          return "Transition";
        if (e & ys)
          return "Retry";
        if (e & Ss)
          return "SelectiveHydration";
        if (e & Es)
          return "IdleHydration";
        if (e & xu)
          return "Idle";
        if (e & Zr)
          return "Offscreen";
      }
    }
    var Zt = -1, bu = Ru, Gc = wu;
    function Cs(e) {
      switch (Ul(e)) {
        case Be:
          return Be;
        case Nl:
          return Nl;
        case ri:
          return ri;
        case Rr:
          return Rr;
        case xn:
          return xn;
        case Xi:
          return Xi;
        case Ru:
        case zc:
        case Uc:
        case Ac:
        case jc:
        case Fc:
        case Hc:
        case Pc:
        case Vc:
        case Tu:
        case Bc:
        case yo:
        case go:
        case Ic:
        case ms:
        case Yc:
          return e & zl;
        case wu:
        case $c:
        case gs:
        case Qc:
        case Wc:
          return e & ys;
        case Ss:
          return Ss;
        case Es:
          return Es;
        case xu:
          return xu;
        case Zr:
          return Zr;
        default:
          return S("Should have found matching lanes. This is a bug in React."), e;
      }
    }
    function Kc(e, t) {
      var a = e.pendingLanes;
      if (a === $)
        return $;
      var i = $, u = e.suspendedLanes, s = e.pingedLanes, f = a & _d;
      if (f !== $) {
        var p = f & ~u;
        if (p !== $)
          i = Cs(p);
        else {
          var v = f & s;
          v !== $ && (i = Cs(v));
        }
      } else {
        var y = a & ~u;
        y !== $ ? i = Cs(y) : s !== $ && (i = Cs(s));
      }
      if (i === $)
        return $;
      if (t !== $ && t !== i && // If we already suspended with a delay, then interrupting is fine. Don't
      // bother waiting until the root is complete.
      (t & u) === $) {
        var g = Ul(i), b = Ul(t);
        if (
          // Tests whether the next lane is equal or lower priority than the wip
          // one. This works because the bits decrease in priority as you go left.
          g >= b || // Default priority updates should not interrupt transition updates. The
          // only difference between default updates and transition updates is that
          // default updates do not support refresh transitions.
          g === xn && (b & zl) !== $
        )
          return t;
      }
      (i & ri) !== $ && (i |= a & xn);
      var w = e.entangledLanes;
      if (w !== $)
        for (var N = e.entanglements, A = i & w; A > 0; ) {
          var H = An(A), ue = 1 << H;
          i |= N[H], A &= ~ue;
        }
      return i;
    }
    function ai(e, t) {
      for (var a = e.eventTimes, i = Zt; t > 0; ) {
        var u = An(t), s = 1 << u, f = a[u];
        f > i && (i = f), t &= ~s;
      }
      return i;
    }
    function kd(e, t) {
      switch (e) {
        case Be:
        case Nl:
        case ri:
          return t + 250;
        case Rr:
        case xn:
        case Xi:
        case Ru:
        case zc:
        case Uc:
        case Ac:
        case jc:
        case Fc:
        case Hc:
        case Pc:
        case Vc:
        case Tu:
        case Bc:
        case yo:
        case go:
        case Ic:
        case ms:
        case Yc:
          return t + 5e3;
        case wu:
        case $c:
        case gs:
        case Qc:
        case Wc:
          return Zt;
        case Ss:
        case Es:
        case xu:
        case Zr:
          return Zt;
        default:
          return S("Should have found matching lanes. This is a bug in React."), Zt;
      }
    }
    function qc(e, t) {
      for (var a = e.pendingLanes, i = e.suspendedLanes, u = e.pingedLanes, s = e.expirationTimes, f = a; f > 0; ) {
        var p = An(f), v = 1 << p, y = s[p];
        y === Zt ? ((v & i) === $ || (v & u) !== $) && (s[p] = kd(v, t)) : y <= t && (e.expiredLanes |= v), f &= ~v;
      }
    }
    function jv(e) {
      return Cs(e.pendingLanes);
    }
    function Xc(e) {
      var t = e.pendingLanes & ~Zr;
      return t !== $ ? t : t & Zr ? Zr : $;
    }
    function Fv(e) {
      return (e & Be) !== $;
    }
    function Rs(e) {
      return (e & _d) !== $;
    }
    function _u(e) {
      return (e & ys) === e;
    }
    function Dd(e) {
      var t = Be | ri | xn;
      return (e & t) === $;
    }
    function Od(e) {
      return (e & zl) === e;
    }
    function Zc(e, t) {
      var a = Nl | ri | Rr | xn;
      return (t & a) !== $;
    }
    function Hv(e, t) {
      return (t & e.expiredLanes) !== $;
    }
    function Ld(e) {
      return (e & zl) !== $;
    }
    function Md() {
      var e = bu;
      return bu <<= 1, (bu & zl) === $ && (bu = Ru), e;
    }
    function Pv() {
      var e = Gc;
      return Gc <<= 1, (Gc & ys) === $ && (Gc = wu), e;
    }
    function Ul(e) {
      return e & -e;
    }
    function Ts(e) {
      return Ul(e);
    }
    function An(e) {
      return 31 - Un(e);
    }
    function ur(e) {
      return An(e);
    }
    function Jr(e, t) {
      return (e & t) !== $;
    }
    function ku(e, t) {
      return (e & t) === t;
    }
    function et(e, t) {
      return e | t;
    }
    function ws(e, t) {
      return e & ~t;
    }
    function Nd(e, t) {
      return e & t;
    }
    function Vv(e) {
      return e;
    }
    function Bv(e, t) {
      return e !== Dt && e < t ? e : t;
    }
    function xs(e) {
      for (var t = [], a = 0; a < Cu; a++)
        t.push(e);
      return t;
    }
    function So(e, t, a) {
      e.pendingLanes |= t, t !== xu && (e.suspendedLanes = $, e.pingedLanes = $);
      var i = e.eventTimes, u = ur(t);
      i[u] = a;
    }
    function Iv(e, t) {
      e.suspendedLanes |= t, e.pingedLanes &= ~t;
      for (var a = e.expirationTimes, i = t; i > 0; ) {
        var u = An(i), s = 1 << u;
        a[u] = Zt, i &= ~s;
      }
    }
    function Jc(e, t, a) {
      e.pingedLanes |= e.suspendedLanes & t;
    }
    function zd(e, t) {
      var a = e.pendingLanes & ~t;
      e.pendingLanes = t, e.suspendedLanes = $, e.pingedLanes = $, e.expiredLanes &= t, e.mutableReadLanes &= t, e.entangledLanes &= t;
      for (var i = e.entanglements, u = e.eventTimes, s = e.expirationTimes, f = a; f > 0; ) {
        var p = An(f), v = 1 << p;
        i[p] = $, u[p] = Zt, s[p] = Zt, f &= ~v;
      }
    }
    function ef(e, t) {
      for (var a = e.entangledLanes |= t, i = e.entanglements, u = a; u; ) {
        var s = An(u), f = 1 << s;
        // Is this one of the newly entangled lanes?
        f & t | // Is this lane transitively entangled with the newly entangled lanes?
        i[s] & t && (i[s] |= t), u &= ~f;
      }
    }
    function Ud(e, t) {
      var a = Ul(t), i;
      switch (a) {
        case ri:
          i = Nl;
          break;
        case xn:
          i = Rr;
          break;
        case Ru:
        case zc:
        case Uc:
        case Ac:
        case jc:
        case Fc:
        case Hc:
        case Pc:
        case Vc:
        case Tu:
        case Bc:
        case yo:
        case go:
        case Ic:
        case ms:
        case Yc:
        case wu:
        case $c:
        case gs:
        case Qc:
        case Wc:
          i = Xi;
          break;
        case xu:
          i = Es;
          break;
        default:
          i = Dt;
          break;
      }
      return (i & (e.suspendedLanes | t)) !== Dt ? Dt : i;
    }
    function bs(e, t, a) {
      if (Xr)
        for (var i = e.pendingUpdatersLaneMap; a > 0; ) {
          var u = ur(a), s = 1 << u, f = i[u];
          f.add(t), a &= ~s;
        }
    }
    function Yv(e, t) {
      if (Xr)
        for (var a = e.pendingUpdatersLaneMap, i = e.memoizedUpdaters; t > 0; ) {
          var u = ur(t), s = 1 << u, f = a[u];
          f.size > 0 && (f.forEach(function(p) {
            var v = p.alternate;
            (v === null || !i.has(v)) && i.add(p);
          }), f.clear()), t &= ~s;
        }
    }
    function Ad(e, t) {
      return null;
    }
    var Lr = Be, _i = ri, Na = xn, za = xu, _s = Dt;
    function Ua() {
      return _s;
    }
    function jn(e) {
      _s = e;
    }
    function $v(e, t) {
      var a = _s;
      try {
        return _s = e, t();
      } finally {
        _s = a;
      }
    }
    function Qv(e, t) {
      return e !== 0 && e < t ? e : t;
    }
    function ks(e, t) {
      return e > t ? e : t;
    }
    function Jn(e, t) {
      return e !== 0 && e < t;
    }
    function Wv(e) {
      var t = Ul(e);
      return Jn(Lr, t) ? Jn(_i, t) ? Rs(t) ? Na : za : _i : Lr;
    }
    function tf(e) {
      var t = e.current.memoizedState;
      return t.isDehydrated;
    }
    var Ds;
    function Tr(e) {
      Ds = e;
    }
    function ly(e) {
      Ds(e);
    }
    var ve;
    function Eo(e) {
      ve = e;
    }
    var nf;
    function Gv(e) {
      nf = e;
    }
    var Kv;
    function Os(e) {
      Kv = e;
    }
    var Ls;
    function jd(e) {
      Ls = e;
    }
    var rf = !1, Ms = [], Zi = null, ki = null, Di = null, bn = /* @__PURE__ */ new Map(), Mr = /* @__PURE__ */ new Map(), Nr = [], qv = [
      "mousedown",
      "mouseup",
      "touchcancel",
      "touchend",
      "touchstart",
      "auxclick",
      "dblclick",
      "pointercancel",
      "pointerdown",
      "pointerup",
      "dragend",
      "dragstart",
      "drop",
      "compositionend",
      "compositionstart",
      "keydown",
      "keypress",
      "keyup",
      "input",
      "textInput",
      // Intentionally camelCase
      "copy",
      "cut",
      "paste",
      "click",
      "change",
      "contextmenu",
      "reset",
      "submit"
    ];
    function Xv(e) {
      return qv.indexOf(e) > -1;
    }
    function ii(e, t, a, i, u) {
      return {
        blockedOn: e,
        domEventName: t,
        eventSystemFlags: a,
        nativeEvent: u,
        targetContainers: [i]
      };
    }
    function Fd(e, t) {
      switch (e) {
        case "focusin":
        case "focusout":
          Zi = null;
          break;
        case "dragenter":
        case "dragleave":
          ki = null;
          break;
        case "mouseover":
        case "mouseout":
          Di = null;
          break;
        case "pointerover":
        case "pointerout": {
          var a = t.pointerId;
          bn.delete(a);
          break;
        }
        case "gotpointercapture":
        case "lostpointercapture": {
          var i = t.pointerId;
          Mr.delete(i);
          break;
        }
      }
    }
    function ea(e, t, a, i, u, s) {
      if (e === null || e.nativeEvent !== s) {
        var f = ii(t, a, i, u, s);
        if (t !== null) {
          var p = Do(t);
          p !== null && ve(p);
        }
        return f;
      }
      e.eventSystemFlags |= i;
      var v = e.targetContainers;
      return u !== null && v.indexOf(u) === -1 && v.push(u), e;
    }
    function uy(e, t, a, i, u) {
      switch (t) {
        case "focusin": {
          var s = u;
          return Zi = ea(Zi, e, t, a, i, s), !0;
        }
        case "dragenter": {
          var f = u;
          return ki = ea(ki, e, t, a, i, f), !0;
        }
        case "mouseover": {
          var p = u;
          return Di = ea(Di, e, t, a, i, p), !0;
        }
        case "pointerover": {
          var v = u, y = v.pointerId;
          return bn.set(y, ea(bn.get(y) || null, e, t, a, i, v)), !0;
        }
        case "gotpointercapture": {
          var g = u, b = g.pointerId;
          return Mr.set(b, ea(Mr.get(b) || null, e, t, a, i, g)), !0;
        }
      }
      return !1;
    }
    function Hd(e) {
      var t = Ys(e.target);
      if (t !== null) {
        var a = da(t);
        if (a !== null) {
          var i = a.tag;
          if (i === ke) {
            var u = wi(a);
            if (u !== null) {
              e.blockedOn = u, Ls(e.priority, function() {
                nf(a);
              });
              return;
            }
          } else if (i === J) {
            var s = a.stateNode;
            if (tf(s)) {
              e.blockedOn = xi(a);
              return;
            }
          }
        }
      }
      e.blockedOn = null;
    }
    function Zv(e) {
      for (var t = Kv(), a = {
        blockedOn: null,
        target: e,
        priority: t
      }, i = 0; i < Nr.length && Jn(t, Nr[i].priority); i++)
        ;
      Nr.splice(i, 0, a), i === 0 && Hd(a);
    }
    function Ns(e) {
      if (e.blockedOn !== null)
        return !1;
      for (var t = e.targetContainers; t.length > 0; ) {
        var a = t[0], i = Ro(e.domEventName, e.eventSystemFlags, a, e.nativeEvent);
        if (i === null) {
          var u = e.nativeEvent, s = new u.constructor(u.type, u);
          ty(s), u.target.dispatchEvent(s), ny();
        } else {
          var f = Do(i);
          return f !== null && ve(f), e.blockedOn = i, !1;
        }
        t.shift();
      }
      return !0;
    }
    function Pd(e, t, a) {
      Ns(e) && a.delete(t);
    }
    function oy() {
      rf = !1, Zi !== null && Ns(Zi) && (Zi = null), ki !== null && Ns(ki) && (ki = null), Di !== null && Ns(Di) && (Di = null), bn.forEach(Pd), Mr.forEach(Pd);
    }
    function Al(e, t) {
      e.blockedOn === t && (e.blockedOn = null, rf || (rf = !0, j.unstable_scheduleCallback(j.unstable_NormalPriority, oy)));
    }
    function Du(e) {
      if (Ms.length > 0) {
        Al(Ms[0], e);
        for (var t = 1; t < Ms.length; t++) {
          var a = Ms[t];
          a.blockedOn === e && (a.blockedOn = null);
        }
      }
      Zi !== null && Al(Zi, e), ki !== null && Al(ki, e), Di !== null && Al(Di, e);
      var i = function(p) {
        return Al(p, e);
      };
      bn.forEach(i), Mr.forEach(i);
      for (var u = 0; u < Nr.length; u++) {
        var s = Nr[u];
        s.blockedOn === e && (s.blockedOn = null);
      }
      for (; Nr.length > 0; ) {
        var f = Nr[0];
        if (f.blockedOn !== null)
          break;
        Hd(f), f.blockedOn === null && Nr.shift();
      }
    }
    var or = k.ReactCurrentBatchConfig, Rt = !0;
    function Wn(e) {
      Rt = !!e;
    }
    function Fn() {
      return Rt;
    }
    function sr(e, t, a) {
      var i = af(t), u;
      switch (i) {
        case Lr:
          u = ma;
          break;
        case _i:
          u = Co;
          break;
        case Na:
        default:
          u = _n;
          break;
      }
      return u.bind(null, t, a, e);
    }
    function ma(e, t, a, i) {
      var u = Ua(), s = or.transition;
      or.transition = null;
      try {
        jn(Lr), _n(e, t, a, i);
      } finally {
        jn(u), or.transition = s;
      }
    }
    function Co(e, t, a, i) {
      var u = Ua(), s = or.transition;
      or.transition = null;
      try {
        jn(_i), _n(e, t, a, i);
      } finally {
        jn(u), or.transition = s;
      }
    }
    function _n(e, t, a, i) {
      Rt && zs(e, t, a, i);
    }
    function zs(e, t, a, i) {
      var u = Ro(e, t, a, i);
      if (u === null) {
        xy(e, t, i, Oi, a), Fd(e, i);
        return;
      }
      if (uy(u, e, t, a, i)) {
        i.stopPropagation();
        return;
      }
      if (Fd(e, i), t & _a && Xv(e)) {
        for (; u !== null; ) {
          var s = Do(u);
          s !== null && ly(s);
          var f = Ro(e, t, a, i);
          if (f === null && xy(e, t, i, Oi, a), f === u)
            break;
          u = f;
        }
        u !== null && i.stopPropagation();
        return;
      }
      xy(e, t, i, null, a);
    }
    var Oi = null;
    function Ro(e, t, a, i) {
      Oi = null;
      var u = dd(i), s = Ys(u);
      if (s !== null) {
        var f = da(s);
        if (f === null)
          s = null;
        else {
          var p = f.tag;
          if (p === ke) {
            var v = wi(f);
            if (v !== null)
              return v;
            s = null;
          } else if (p === J) {
            var y = f.stateNode;
            if (tf(y))
              return xi(f);
            s = null;
          } else f !== s && (s = null);
        }
      }
      return Oi = s, null;
    }
    function af(e) {
      switch (e) {
        case "cancel":
        case "click":
        case "close":
        case "contextmenu":
        case "copy":
        case "cut":
        case "auxclick":
        case "dblclick":
        case "dragend":
        case "dragstart":
        case "drop":
        case "focusin":
        case "focusout":
        case "input":
        case "invalid":
        case "keydown":
        case "keypress":
        case "keyup":
        case "mousedown":
        case "mouseup":
        case "paste":
        case "pause":
        case "play":
        case "pointercancel":
        case "pointerdown":
        case "pointerup":
        case "ratechange":
        case "reset":
        case "resize":
        case "seeked":
        case "submit":
        case "touchcancel":
        case "touchend":
        case "touchstart":
        case "volumechange":
        case "change":
        case "selectionchange":
        case "textInput":
        case "compositionstart":
        case "compositionend":
        case "compositionupdate":
        case "beforeblur":
        case "afterblur":
        case "beforeinput":
        case "blur":
        case "fullscreenchange":
        case "focus":
        case "hashchange":
        case "popstate":
        case "select":
        case "selectstart":
          return Lr;
        case "drag":
        case "dragenter":
        case "dragexit":
        case "dragleave":
        case "dragover":
        case "mousemove":
        case "mouseout":
        case "mouseover":
        case "pointermove":
        case "pointerout":
        case "pointerover":
        case "scroll":
        case "toggle":
        case "touchmove":
        case "wheel":
        case "mouseenter":
        case "mouseleave":
        case "pointerenter":
        case "pointerleave":
          return _i;
        case "message": {
          var t = kc();
          switch (t) {
            case ss:
              return Lr;
            case Ll:
              return _i;
            case Ki:
            case iy:
              return Na;
            case mu:
              return za;
            default:
              return Na;
          }
        }
        default:
          return Na;
      }
    }
    function Us(e, t, a) {
      return e.addEventListener(t, a, !1), a;
    }
    function ta(e, t, a) {
      return e.addEventListener(t, a, !0), a;
    }
    function Vd(e, t, a, i) {
      return e.addEventListener(t, a, {
        capture: !0,
        passive: i
      }), a;
    }
    function To(e, t, a, i) {
      return e.addEventListener(t, a, {
        passive: i
      }), a;
    }
    var ya = null, wo = null, Ou = null;
    function jl(e) {
      return ya = e, wo = As(), !0;
    }
    function lf() {
      ya = null, wo = null, Ou = null;
    }
    function Ji() {
      if (Ou)
        return Ou;
      var e, t = wo, a = t.length, i, u = As(), s = u.length;
      for (e = 0; e < a && t[e] === u[e]; e++)
        ;
      var f = a - e;
      for (i = 1; i <= f && t[a - i] === u[s - i]; i++)
        ;
      var p = i > 1 ? 1 - i : void 0;
      return Ou = u.slice(e, p), Ou;
    }
    function As() {
      return "value" in ya ? ya.value : ya.textContent;
    }
    function Fl(e) {
      var t, a = e.keyCode;
      return "charCode" in e ? (t = e.charCode, t === 0 && a === 13 && (t = 13)) : t = a, t === 10 && (t = 13), t >= 32 || t === 13 ? t : 0;
    }
    function xo() {
      return !0;
    }
    function js() {
      return !1;
    }
    function wr(e) {
      function t(a, i, u, s, f) {
        this._reactName = a, this._targetInst = u, this.type = i, this.nativeEvent = s, this.target = f, this.currentTarget = null;
        for (var p in e)
          if (e.hasOwnProperty(p)) {
            var v = e[p];
            v ? this[p] = v(s) : this[p] = s[p];
          }
        var y = s.defaultPrevented != null ? s.defaultPrevented : s.returnValue === !1;
        return y ? this.isDefaultPrevented = xo : this.isDefaultPrevented = js, this.isPropagationStopped = js, this;
      }
      return rt(t.prototype, {
        preventDefault: function() {
          this.defaultPrevented = !0;
          var a = this.nativeEvent;
          a && (a.preventDefault ? a.preventDefault() : typeof a.returnValue != "unknown" && (a.returnValue = !1), this.isDefaultPrevented = xo);
        },
        stopPropagation: function() {
          var a = this.nativeEvent;
          a && (a.stopPropagation ? a.stopPropagation() : typeof a.cancelBubble != "unknown" && (a.cancelBubble = !0), this.isPropagationStopped = xo);
        },
        /**
         * We release all dispatched `SyntheticEvent`s after each event loop, adding
         * them back into the pool. This allows a way to hold onto a reference that
         * won't be added back into the pool.
         */
        persist: function() {
        },
        /**
         * Checks if this event should be released back into the pool.
         *
         * @return {boolean} True if this should not be released, false otherwise.
         */
        isPersistent: xo
      }), t;
    }
    var Hn = {
      eventPhase: 0,
      bubbles: 0,
      cancelable: 0,
      timeStamp: function(e) {
        return e.timeStamp || Date.now();
      },
      defaultPrevented: 0,
      isTrusted: 0
    }, Li = wr(Hn), zr = rt({}, Hn, {
      view: 0,
      detail: 0
    }), na = wr(zr), uf, Fs, Lu;
    function sy(e) {
      e !== Lu && (Lu && e.type === "mousemove" ? (uf = e.screenX - Lu.screenX, Fs = e.screenY - Lu.screenY) : (uf = 0, Fs = 0), Lu = e);
    }
    var li = rt({}, zr, {
      screenX: 0,
      screenY: 0,
      clientX: 0,
      clientY: 0,
      pageX: 0,
      pageY: 0,
      ctrlKey: 0,
      shiftKey: 0,
      altKey: 0,
      metaKey: 0,
      getModifierState: pn,
      button: 0,
      buttons: 0,
      relatedTarget: function(e) {
        return e.relatedTarget === void 0 ? e.fromElement === e.srcElement ? e.toElement : e.fromElement : e.relatedTarget;
      },
      movementX: function(e) {
        return "movementX" in e ? e.movementX : (sy(e), uf);
      },
      movementY: function(e) {
        return "movementY" in e ? e.movementY : Fs;
      }
    }), Bd = wr(li), Id = rt({}, li, {
      dataTransfer: 0
    }), Mu = wr(Id), Yd = rt({}, zr, {
      relatedTarget: 0
    }), el = wr(Yd), Jv = rt({}, Hn, {
      animationName: 0,
      elapsedTime: 0,
      pseudoElement: 0
    }), eh = wr(Jv), $d = rt({}, Hn, {
      clipboardData: function(e) {
        return "clipboardData" in e ? e.clipboardData : window.clipboardData;
      }
    }), of = wr($d), cy = rt({}, Hn, {
      data: 0
    }), th = wr(cy), nh = th, rh = {
      Esc: "Escape",
      Spacebar: " ",
      Left: "ArrowLeft",
      Up: "ArrowUp",
      Right: "ArrowRight",
      Down: "ArrowDown",
      Del: "Delete",
      Win: "OS",
      Menu: "ContextMenu",
      Apps: "ContextMenu",
      Scroll: "ScrollLock",
      MozPrintableKey: "Unidentified"
    }, Nu = {
      8: "Backspace",
      9: "Tab",
      12: "Clear",
      13: "Enter",
      16: "Shift",
      17: "Control",
      18: "Alt",
      19: "Pause",
      20: "CapsLock",
      27: "Escape",
      32: " ",
      33: "PageUp",
      34: "PageDown",
      35: "End",
      36: "Home",
      37: "ArrowLeft",
      38: "ArrowUp",
      39: "ArrowRight",
      40: "ArrowDown",
      45: "Insert",
      46: "Delete",
      112: "F1",
      113: "F2",
      114: "F3",
      115: "F4",
      116: "F5",
      117: "F6",
      118: "F7",
      119: "F8",
      120: "F9",
      121: "F10",
      122: "F11",
      123: "F12",
      144: "NumLock",
      145: "ScrollLock",
      224: "Meta"
    };
    function fy(e) {
      if (e.key) {
        var t = rh[e.key] || e.key;
        if (t !== "Unidentified")
          return t;
      }
      if (e.type === "keypress") {
        var a = Fl(e);
        return a === 13 ? "Enter" : String.fromCharCode(a);
      }
      return e.type === "keydown" || e.type === "keyup" ? Nu[e.keyCode] || "Unidentified" : "";
    }
    var bo = {
      Alt: "altKey",
      Control: "ctrlKey",
      Meta: "metaKey",
      Shift: "shiftKey"
    };
    function ah(e) {
      var t = this, a = t.nativeEvent;
      if (a.getModifierState)
        return a.getModifierState(e);
      var i = bo[e];
      return i ? !!a[i] : !1;
    }
    function pn(e) {
      return ah;
    }
    var dy = rt({}, zr, {
      key: fy,
      code: 0,
      location: 0,
      ctrlKey: 0,
      shiftKey: 0,
      altKey: 0,
      metaKey: 0,
      repeat: 0,
      locale: 0,
      getModifierState: pn,
      // Legacy Interface
      charCode: function(e) {
        return e.type === "keypress" ? Fl(e) : 0;
      },
      keyCode: function(e) {
        return e.type === "keydown" || e.type === "keyup" ? e.keyCode : 0;
      },
      which: function(e) {
        return e.type === "keypress" ? Fl(e) : e.type === "keydown" || e.type === "keyup" ? e.keyCode : 0;
      }
    }), ih = wr(dy), py = rt({}, li, {
      pointerId: 0,
      width: 0,
      height: 0,
      pressure: 0,
      tangentialPressure: 0,
      tiltX: 0,
      tiltY: 0,
      twist: 0,
      pointerType: 0,
      isPrimary: 0
    }), lh = wr(py), uh = rt({}, zr, {
      touches: 0,
      targetTouches: 0,
      changedTouches: 0,
      altKey: 0,
      metaKey: 0,
      ctrlKey: 0,
      shiftKey: 0,
      getModifierState: pn
    }), oh = wr(uh), vy = rt({}, Hn, {
      propertyName: 0,
      elapsedTime: 0,
      pseudoElement: 0
    }), Aa = wr(vy), Qd = rt({}, li, {
      deltaX: function(e) {
        return "deltaX" in e ? e.deltaX : (
          // Fallback to `wheelDeltaX` for Webkit and normalize (right is positive).
          "wheelDeltaX" in e ? -e.wheelDeltaX : 0
        );
      },
      deltaY: function(e) {
        return "deltaY" in e ? e.deltaY : (
          // Fallback to `wheelDeltaY` for Webkit and normalize (down is positive).
          "wheelDeltaY" in e ? -e.wheelDeltaY : (
            // Fallback to `wheelDelta` for IE<9 and normalize (down is positive).
            "wheelDelta" in e ? -e.wheelDelta : 0
          )
        );
      },
      deltaZ: 0,
      // Browsers without "deltaMode" is reporting in raw wheel delta where one
      // notch on the scroll is always +/- 120, roughly equivalent to pixels.
      // A good approximation of DOM_DELTA_LINE (1) is 5% of viewport size or
      // ~40 pixels, for DOM_DELTA_SCREEN (2) it is 87.5% of viewport size.
      deltaMode: 0
    }), hy = wr(Qd), Hl = [9, 13, 27, 32], Hs = 229, tl = On && "CompositionEvent" in window, Pl = null;
    On && "documentMode" in document && (Pl = document.documentMode);
    var Wd = On && "TextEvent" in window && !Pl, sf = On && (!tl || Pl && Pl > 8 && Pl <= 11), sh = 32, cf = String.fromCharCode(sh);
    function my() {
      dt("onBeforeInput", ["compositionend", "keypress", "textInput", "paste"]), dt("onCompositionEnd", ["compositionend", "focusout", "keydown", "keypress", "keyup", "mousedown"]), dt("onCompositionStart", ["compositionstart", "focusout", "keydown", "keypress", "keyup", "mousedown"]), dt("onCompositionUpdate", ["compositionupdate", "focusout", "keydown", "keypress", "keyup", "mousedown"]);
    }
    var Gd = !1;
    function ch(e) {
      return (e.ctrlKey || e.altKey || e.metaKey) && // ctrlKey && altKey is equivalent to AltGr, and is not a command.
      !(e.ctrlKey && e.altKey);
    }
    function ff(e) {
      switch (e) {
        case "compositionstart":
          return "onCompositionStart";
        case "compositionend":
          return "onCompositionEnd";
        case "compositionupdate":
          return "onCompositionUpdate";
      }
    }
    function df(e, t) {
      return e === "keydown" && t.keyCode === Hs;
    }
    function Kd(e, t) {
      switch (e) {
        case "keyup":
          return Hl.indexOf(t.keyCode) !== -1;
        case "keydown":
          return t.keyCode !== Hs;
        case "keypress":
        case "mousedown":
        case "focusout":
          return !0;
        default:
          return !1;
      }
    }
    function pf(e) {
      var t = e.detail;
      return typeof t == "object" && "data" in t ? t.data : null;
    }
    function fh(e) {
      return e.locale === "ko";
    }
    var zu = !1;
    function qd(e, t, a, i, u) {
      var s, f;
      if (tl ? s = ff(t) : zu ? Kd(t, i) && (s = "onCompositionEnd") : df(t, i) && (s = "onCompositionStart"), !s)
        return null;
      sf && !fh(i) && (!zu && s === "onCompositionStart" ? zu = jl(u) : s === "onCompositionEnd" && zu && (f = Ji()));
      var p = gh(a, s);
      if (p.length > 0) {
        var v = new th(s, t, null, i, u);
        if (e.push({
          event: v,
          listeners: p
        }), f)
          v.data = f;
        else {
          var y = pf(i);
          y !== null && (v.data = y);
        }
      }
    }
    function vf(e, t) {
      switch (e) {
        case "compositionend":
          return pf(t);
        case "keypress":
          var a = t.which;
          return a !== sh ? null : (Gd = !0, cf);
        case "textInput":
          var i = t.data;
          return i === cf && Gd ? null : i;
        default:
          return null;
      }
    }
    function Xd(e, t) {
      if (zu) {
        if (e === "compositionend" || !tl && Kd(e, t)) {
          var a = Ji();
          return lf(), zu = !1, a;
        }
        return null;
      }
      switch (e) {
        case "paste":
          return null;
        case "keypress":
          if (!ch(t)) {
            if (t.char && t.char.length > 1)
              return t.char;
            if (t.which)
              return String.fromCharCode(t.which);
          }
          return null;
        case "compositionend":
          return sf && !fh(t) ? null : t.data;
        default:
          return null;
      }
    }
    function hf(e, t, a, i, u) {
      var s;
      if (Wd ? s = vf(t, i) : s = Xd(t, i), !s)
        return null;
      var f = gh(a, "onBeforeInput");
      if (f.length > 0) {
        var p = new nh("onBeforeInput", "beforeinput", null, i, u);
        e.push({
          event: p,
          listeners: f
        }), p.data = s;
      }
    }
    function dh(e, t, a, i, u, s, f) {
      qd(e, t, a, i, u), hf(e, t, a, i, u);
    }
    var yy = {
      color: !0,
      date: !0,
      datetime: !0,
      "datetime-local": !0,
      email: !0,
      month: !0,
      number: !0,
      password: !0,
      range: !0,
      search: !0,
      tel: !0,
      text: !0,
      time: !0,
      url: !0,
      week: !0
    };
    function Ps(e) {
      var t = e && e.nodeName && e.nodeName.toLowerCase();
      return t === "input" ? !!yy[e.type] : t === "textarea";
    }
    /**
     * Checks if an event is supported in the current execution environment.
     *
     * NOTE: This will not work correctly for non-generic events such as `change`,
     * `reset`, `load`, `error`, and `select`.
     *
     * Borrows from Modernizr.
     *
     * @param {string} eventNameSuffix Event name, e.g. "click".
     * @return {boolean} True if the event is supported.
     * @internal
     * @license Modernizr 3.0.0pre (Custom Build) | MIT
     */
    function gy(e) {
      if (!On)
        return !1;
      var t = "on" + e, a = t in document;
      if (!a) {
        var i = document.createElement("div");
        i.setAttribute(t, "return;"), a = typeof i[t] == "function";
      }
      return a;
    }
    function Vs() {
      dt("onChange", ["change", "click", "focusin", "focusout", "input", "keydown", "keyup", "selectionchange"]);
    }
    function ph(e, t, a, i) {
      oo(i);
      var u = gh(t, "onChange");
      if (u.length > 0) {
        var s = new Li("onChange", "change", null, a, i);
        e.push({
          event: s,
          listeners: u
        });
      }
    }
    var Vl = null, n = null;
    function r(e) {
      var t = e.nodeName && e.nodeName.toLowerCase();
      return t === "select" || t === "input" && e.type === "file";
    }
    function l(e) {
      var t = [];
      ph(t, n, e, dd(e)), xv(o, t);
    }
    function o(e) {
      bE(e, 0);
    }
    function c(e) {
      var t = Cf(e);
      if (gi(t))
        return e;
    }
    function d(e, t) {
      if (e === "change")
        return t;
    }
    var m = !1;
    On && (m = gy("input") && (!document.documentMode || document.documentMode > 9));
    function E(e, t) {
      Vl = e, n = t, Vl.attachEvent("onpropertychange", U);
    }
    function T() {
      Vl && (Vl.detachEvent("onpropertychange", U), Vl = null, n = null);
    }
    function U(e) {
      e.propertyName === "value" && c(n) && l(e);
    }
    function W(e, t, a) {
      e === "focusin" ? (T(), E(t, a)) : e === "focusout" && T();
    }
    function K(e, t) {
      if (e === "selectionchange" || e === "keyup" || e === "keydown")
        return c(n);
    }
    function Q(e) {
      var t = e.nodeName;
      return t && t.toLowerCase() === "input" && (e.type === "checkbox" || e.type === "radio");
    }
    function fe(e, t) {
      if (e === "click")
        return c(t);
    }
    function me(e, t) {
      if (e === "input" || e === "change")
        return c(t);
    }
    function Ce(e) {
      var t = e._wrapperState;
      !t || !t.controlled || e.type !== "number" || Ne(e, "number", e.value);
    }
    function kn(e, t, a, i, u, s, f) {
      var p = a ? Cf(a) : window, v, y;
      if (r(p) ? v = d : Ps(p) ? m ? v = me : (v = K, y = W) : Q(p) && (v = fe), v) {
        var g = v(t, a);
        if (g) {
          ph(e, g, i, u);
          return;
        }
      }
      y && y(t, p, a), t === "focusout" && Ce(p);
    }
    function D() {
      It("onMouseEnter", ["mouseout", "mouseover"]), It("onMouseLeave", ["mouseout", "mouseover"]), It("onPointerEnter", ["pointerout", "pointerover"]), It("onPointerLeave", ["pointerout", "pointerover"]);
    }
    function x(e, t, a, i, u, s, f) {
      var p = t === "mouseover" || t === "pointerover", v = t === "mouseout" || t === "pointerout";
      if (p && !rs(i)) {
        var y = i.relatedTarget || i.fromElement;
        if (y && (Ys(y) || fp(y)))
          return;
      }
      if (!(!v && !p)) {
        var g;
        if (u.window === u)
          g = u;
        else {
          var b = u.ownerDocument;
          b ? g = b.defaultView || b.parentWindow : g = window;
        }
        var w, N;
        if (v) {
          var A = i.relatedTarget || i.toElement;
          if (w = a, N = A ? Ys(A) : null, N !== null) {
            var H = da(N);
            (N !== H || N.tag !== ae && N.tag !== Ve) && (N = null);
          }
        } else
          w = null, N = a;
        if (w !== N) {
          var ue = Bd, ze = "onMouseLeave", be = "onMouseEnter", wt = "mouse";
          (t === "pointerout" || t === "pointerover") && (ue = lh, ze = "onPointerLeave", be = "onPointerEnter", wt = "pointer");
          var yt = w == null ? g : Cf(w), O = N == null ? g : Cf(N), P = new ue(ze, wt + "leave", w, i, u);
          P.target = yt, P.relatedTarget = O;
          var L = null, q = Ys(u);
          if (q === a) {
            var pe = new ue(be, wt + "enter", N, i, u);
            pe.target = O, pe.relatedTarget = yt, L = pe;
          }
          _T(e, P, L, w, N);
        }
      }
    }
    function M(e, t) {
      return e === t && (e !== 0 || 1 / e === 1 / t) || e !== e && t !== t;
    }
    var G = typeof Object.is == "function" ? Object.is : M;
    function ye(e, t) {
      if (G(e, t))
        return !0;
      if (typeof e != "object" || e === null || typeof t != "object" || t === null)
        return !1;
      var a = Object.keys(e), i = Object.keys(t);
      if (a.length !== i.length)
        return !1;
      for (var u = 0; u < a.length; u++) {
        var s = a[u];
        if (!xr.call(t, s) || !G(e[s], t[s]))
          return !1;
      }
      return !0;
    }
    function Ue(e) {
      for (; e && e.firstChild; )
        e = e.firstChild;
      return e;
    }
    function je(e) {
      for (; e; ) {
        if (e.nextSibling)
          return e.nextSibling;
        e = e.parentNode;
      }
    }
    function $e(e, t) {
      for (var a = Ue(e), i = 0, u = 0; a; ) {
        if (a.nodeType === Yi) {
          if (u = i + a.textContent.length, i <= t && u >= t)
            return {
              node: a,
              offset: t - i
            };
          i = u;
        }
        a = Ue(je(a));
      }
    }
    function er(e) {
      var t = e.ownerDocument, a = t && t.defaultView || window, i = a.getSelection && a.getSelection();
      if (!i || i.rangeCount === 0)
        return null;
      var u = i.anchorNode, s = i.anchorOffset, f = i.focusNode, p = i.focusOffset;
      try {
        u.nodeType, f.nodeType;
      } catch {
        return null;
      }
      return zt(e, u, s, f, p);
    }
    function zt(e, t, a, i, u) {
      var s = 0, f = -1, p = -1, v = 0, y = 0, g = e, b = null;
      e: for (; ; ) {
        for (var w = null; g === t && (a === 0 || g.nodeType === Yi) && (f = s + a), g === i && (u === 0 || g.nodeType === Yi) && (p = s + u), g.nodeType === Yi && (s += g.nodeValue.length), (w = g.firstChild) !== null; )
          b = g, g = w;
        for (; ; ) {
          if (g === e)
            break e;
          if (b === t && ++v === a && (f = s), b === i && ++y === u && (p = s), (w = g.nextSibling) !== null)
            break;
          g = b, b = g.parentNode;
        }
        g = w;
      }
      return f === -1 || p === -1 ? null : {
        start: f,
        end: p
      };
    }
    function Bl(e, t) {
      var a = e.ownerDocument || document, i = a && a.defaultView || window;
      if (i.getSelection) {
        var u = i.getSelection(), s = e.textContent.length, f = Math.min(t.start, s), p = t.end === void 0 ? f : Math.min(t.end, s);
        if (!u.extend && f > p) {
          var v = p;
          p = f, f = v;
        }
        var y = $e(e, f), g = $e(e, p);
        if (y && g) {
          if (u.rangeCount === 1 && u.anchorNode === y.node && u.anchorOffset === y.offset && u.focusNode === g.node && u.focusOffset === g.offset)
            return;
          var b = a.createRange();
          b.setStart(y.node, y.offset), u.removeAllRanges(), f > p ? (u.addRange(b), u.extend(g.node, g.offset)) : (b.setEnd(g.node, g.offset), u.addRange(b));
        }
      }
    }
    function vh(e) {
      return e && e.nodeType === Yi;
    }
    function hE(e, t) {
      return !e || !t ? !1 : e === t ? !0 : vh(e) ? !1 : vh(t) ? hE(e, t.parentNode) : "contains" in e ? e.contains(t) : e.compareDocumentPosition ? !!(e.compareDocumentPosition(t) & 16) : !1;
    }
    function sT(e) {
      return e && e.ownerDocument && hE(e.ownerDocument.documentElement, e);
    }
    function cT(e) {
      try {
        return typeof e.contentWindow.location.href == "string";
      } catch {
        return !1;
      }
    }
    function mE() {
      for (var e = window, t = ba(); t instanceof e.HTMLIFrameElement; ) {
        if (cT(t))
          e = t.contentWindow;
        else
          return t;
        t = ba(e.document);
      }
      return t;
    }
    function Sy(e) {
      var t = e && e.nodeName && e.nodeName.toLowerCase();
      return t && (t === "input" && (e.type === "text" || e.type === "search" || e.type === "tel" || e.type === "url" || e.type === "password") || t === "textarea" || e.contentEditable === "true");
    }
    function fT() {
      var e = mE();
      return {
        focusedElem: e,
        selectionRange: Sy(e) ? pT(e) : null
      };
    }
    function dT(e) {
      var t = mE(), a = e.focusedElem, i = e.selectionRange;
      if (t !== a && sT(a)) {
        i !== null && Sy(a) && vT(a, i);
        for (var u = [], s = a; s = s.parentNode; )
          s.nodeType === Qr && u.push({
            element: s,
            left: s.scrollLeft,
            top: s.scrollTop
          });
        typeof a.focus == "function" && a.focus();
        for (var f = 0; f < u.length; f++) {
          var p = u[f];
          p.element.scrollLeft = p.left, p.element.scrollTop = p.top;
        }
      }
    }
    function pT(e) {
      var t;
      return "selectionStart" in e ? t = {
        start: e.selectionStart,
        end: e.selectionEnd
      } : t = er(e), t || {
        start: 0,
        end: 0
      };
    }
    function vT(e, t) {
      var a = t.start, i = t.end;
      i === void 0 && (i = a), "selectionStart" in e ? (e.selectionStart = a, e.selectionEnd = Math.min(i, e.value.length)) : Bl(e, t);
    }
    var hT = On && "documentMode" in document && document.documentMode <= 11;
    function mT() {
      dt("onSelect", ["focusout", "contextmenu", "dragend", "focusin", "keydown", "keyup", "mousedown", "mouseup", "selectionchange"]);
    }
    var mf = null, Ey = null, Zd = null, Cy = !1;
    function yT(e) {
      if ("selectionStart" in e && Sy(e))
        return {
          start: e.selectionStart,
          end: e.selectionEnd
        };
      var t = e.ownerDocument && e.ownerDocument.defaultView || window, a = t.getSelection();
      return {
        anchorNode: a.anchorNode,
        anchorOffset: a.anchorOffset,
        focusNode: a.focusNode,
        focusOffset: a.focusOffset
      };
    }
    function gT(e) {
      return e.window === e ? e.document : e.nodeType === $i ? e : e.ownerDocument;
    }
    function yE(e, t, a) {
      var i = gT(a);
      if (!(Cy || mf == null || mf !== ba(i))) {
        var u = yT(mf);
        if (!Zd || !ye(Zd, u)) {
          Zd = u;
          var s = gh(Ey, "onSelect");
          if (s.length > 0) {
            var f = new Li("onSelect", "select", null, t, a);
            e.push({
              event: f,
              listeners: s
            }), f.target = mf;
          }
        }
      }
    }
    function ST(e, t, a, i, u, s, f) {
      var p = a ? Cf(a) : window;
      switch (t) {
        case "focusin":
          (Ps(p) || p.contentEditable === "true") && (mf = p, Ey = a, Zd = null);
          break;
        case "focusout":
          mf = null, Ey = null, Zd = null;
          break;
        case "mousedown":
          Cy = !0;
          break;
        case "contextmenu":
        case "mouseup":
        case "dragend":
          Cy = !1, yE(e, i, u);
          break;
        case "selectionchange":
          if (hT)
            break;
        case "keydown":
        case "keyup":
          yE(e, i, u);
      }
    }
    function hh(e, t) {
      var a = {};
      return a[e.toLowerCase()] = t.toLowerCase(), a["Webkit" + e] = "webkit" + t, a["Moz" + e] = "moz" + t, a;
    }
    var yf = {
      animationend: hh("Animation", "AnimationEnd"),
      animationiteration: hh("Animation", "AnimationIteration"),
      animationstart: hh("Animation", "AnimationStart"),
      transitionend: hh("Transition", "TransitionEnd")
    }, Ry = {}, gE = {};
    On && (gE = document.createElement("div").style, "AnimationEvent" in window || (delete yf.animationend.animation, delete yf.animationiteration.animation, delete yf.animationstart.animation), "TransitionEvent" in window || delete yf.transitionend.transition);
    function mh(e) {
      if (Ry[e])
        return Ry[e];
      if (!yf[e])
        return e;
      var t = yf[e];
      for (var a in t)
        if (t.hasOwnProperty(a) && a in gE)
          return Ry[e] = t[a];
      return e;
    }
    var SE = mh("animationend"), EE = mh("animationiteration"), CE = mh("animationstart"), RE = mh("transitionend"), TE = /* @__PURE__ */ new Map(), wE = ["abort", "auxClick", "cancel", "canPlay", "canPlayThrough", "click", "close", "contextMenu", "copy", "cut", "drag", "dragEnd", "dragEnter", "dragExit", "dragLeave", "dragOver", "dragStart", "drop", "durationChange", "emptied", "encrypted", "ended", "error", "gotPointerCapture", "input", "invalid", "keyDown", "keyPress", "keyUp", "load", "loadedData", "loadedMetadata", "loadStart", "lostPointerCapture", "mouseDown", "mouseMove", "mouseOut", "mouseOver", "mouseUp", "paste", "pause", "play", "playing", "pointerCancel", "pointerDown", "pointerMove", "pointerOut", "pointerOver", "pointerUp", "progress", "rateChange", "reset", "resize", "seeked", "seeking", "stalled", "submit", "suspend", "timeUpdate", "touchCancel", "touchEnd", "touchStart", "volumeChange", "scroll", "toggle", "touchMove", "waiting", "wheel"];
    function _o(e, t) {
      TE.set(e, t), dt(t, [e]);
    }
    function ET() {
      for (var e = 0; e < wE.length; e++) {
        var t = wE[e], a = t.toLowerCase(), i = t[0].toUpperCase() + t.slice(1);
        _o(a, "on" + i);
      }
      _o(SE, "onAnimationEnd"), _o(EE, "onAnimationIteration"), _o(CE, "onAnimationStart"), _o("dblclick", "onDoubleClick"), _o("focusin", "onFocus"), _o("focusout", "onBlur"), _o(RE, "onTransitionEnd");
    }
    function CT(e, t, a, i, u, s, f) {
      var p = TE.get(t);
      if (p !== void 0) {
        var v = Li, y = t;
        switch (t) {
          case "keypress":
            if (Fl(i) === 0)
              return;
          case "keydown":
          case "keyup":
            v = ih;
            break;
          case "focusin":
            y = "focus", v = el;
            break;
          case "focusout":
            y = "blur", v = el;
            break;
          case "beforeblur":
          case "afterblur":
            v = el;
            break;
          case "click":
            if (i.button === 2)
              return;
          case "auxclick":
          case "dblclick":
          case "mousedown":
          case "mousemove":
          case "mouseup":
          case "mouseout":
          case "mouseover":
          case "contextmenu":
            v = Bd;
            break;
          case "drag":
          case "dragend":
          case "dragenter":
          case "dragexit":
          case "dragleave":
          case "dragover":
          case "dragstart":
          case "drop":
            v = Mu;
            break;
          case "touchcancel":
          case "touchend":
          case "touchmove":
          case "touchstart":
            v = oh;
            break;
          case SE:
          case EE:
          case CE:
            v = eh;
            break;
          case RE:
            v = Aa;
            break;
          case "scroll":
            v = na;
            break;
          case "wheel":
            v = hy;
            break;
          case "copy":
          case "cut":
          case "paste":
            v = of;
            break;
          case "gotpointercapture":
          case "lostpointercapture":
          case "pointercancel":
          case "pointerdown":
          case "pointermove":
          case "pointerout":
          case "pointerover":
          case "pointerup":
            v = lh;
            break;
        }
        var g = (s & _a) !== 0;
        {
          var b = !g && // TODO: ideally, we'd eventually add all events from
          // nonDelegatedEvents list in DOMPluginEventSystem.
          // Then we can remove this special list.
          // This is a breaking change that can wait until React 18.
          t === "scroll", w = xT(a, p, i.type, g, b);
          if (w.length > 0) {
            var N = new v(p, y, null, i, u);
            e.push({
              event: N,
              listeners: w
            });
          }
        }
      }
    }
    ET(), D(), Vs(), mT(), my();
    function RT(e, t, a, i, u, s, f) {
      CT(e, t, a, i, u, s);
      var p = (s & fd) === 0;
      p && (x(e, t, a, i, u), kn(e, t, a, i, u), ST(e, t, a, i, u), dh(e, t, a, i, u));
    }
    var Jd = ["abort", "canplay", "canplaythrough", "durationchange", "emptied", "encrypted", "ended", "error", "loadeddata", "loadedmetadata", "loadstart", "pause", "play", "playing", "progress", "ratechange", "resize", "seeked", "seeking", "stalled", "suspend", "timeupdate", "volumechange", "waiting"], Ty = new Set(["cancel", "close", "invalid", "load", "scroll", "toggle"].concat(Jd));
    function xE(e, t, a) {
      var i = e.type || "unknown-event";
      e.currentTarget = a, Ci(i, t, void 0, e), e.currentTarget = null;
    }
    function TT(e, t, a) {
      var i;
      if (a)
        for (var u = t.length - 1; u >= 0; u--) {
          var s = t[u], f = s.instance, p = s.currentTarget, v = s.listener;
          if (f !== i && e.isPropagationStopped())
            return;
          xE(e, v, p), i = f;
        }
      else
        for (var y = 0; y < t.length; y++) {
          var g = t[y], b = g.instance, w = g.currentTarget, N = g.listener;
          if (b !== i && e.isPropagationStopped())
            return;
          xE(e, N, w), i = b;
        }
    }
    function bE(e, t) {
      for (var a = (t & _a) !== 0, i = 0; i < e.length; i++) {
        var u = e[i], s = u.event, f = u.listeners;
        TT(s, f, a);
      }
      ls();
    }
    function wT(e, t, a, i, u) {
      var s = dd(a), f = [];
      RT(f, e, i, a, s, t), bE(f, t);
    }
    function Sn(e, t) {
      Ty.has(e) || S('Did not expect a listenToNonDelegatedEvent() call for "%s". This is a bug in React. Please file an issue.', e);
      var a = !1, i = ex(t), u = kT(e);
      i.has(u) || (_E(t, e, hc, a), i.add(u));
    }
    function wy(e, t, a) {
      Ty.has(e) && !t && S('Did not expect a listenToNativeEvent() call for "%s" in the bubble phase. This is a bug in React. Please file an issue.', e);
      var i = 0;
      t && (i |= _a), _E(a, e, i, t);
    }
    var yh = "_reactListening" + Math.random().toString(36).slice(2);
    function ep(e) {
      if (!e[yh]) {
        e[yh] = !0, lt.forEach(function(a) {
          a !== "selectionchange" && (Ty.has(a) || wy(a, !1, e), wy(a, !0, e));
        });
        var t = e.nodeType === $i ? e : e.ownerDocument;
        t !== null && (t[yh] || (t[yh] = !0, wy("selectionchange", !1, t)));
      }
    }
    function _E(e, t, a, i, u) {
      var s = sr(e, t, a), f = void 0;
      is && (t === "touchstart" || t === "touchmove" || t === "wheel") && (f = !0), e = e, i ? f !== void 0 ? Vd(e, t, s, f) : ta(e, t, s) : f !== void 0 ? To(e, t, s, f) : Us(e, t, s);
    }
    function kE(e, t) {
      return e === t || e.nodeType === Mn && e.parentNode === t;
    }
    function xy(e, t, a, i, u) {
      var s = i;
      if (!(t & cd) && !(t & hc)) {
        var f = u;
        if (i !== null) {
          var p = i;
          e: for (; ; ) {
            if (p === null)
              return;
            var v = p.tag;
            if (v === J || v === Se) {
              var y = p.stateNode.containerInfo;
              if (kE(y, f))
                break;
              if (v === Se)
                for (var g = p.return; g !== null; ) {
                  var b = g.tag;
                  if (b === J || b === Se) {
                    var w = g.stateNode.containerInfo;
                    if (kE(w, f))
                      return;
                  }
                  g = g.return;
                }
              for (; y !== null; ) {
                var N = Ys(y);
                if (N === null)
                  return;
                var A = N.tag;
                if (A === ae || A === Ve) {
                  p = s = N;
                  continue e;
                }
                y = y.parentNode;
              }
            }
            p = p.return;
          }
        }
      }
      xv(function() {
        return wT(e, t, a, s);
      });
    }
    function tp(e, t, a) {
      return {
        instance: e,
        listener: t,
        currentTarget: a
      };
    }
    function xT(e, t, a, i, u, s) {
      for (var f = t !== null ? t + "Capture" : null, p = i ? f : t, v = [], y = e, g = null; y !== null; ) {
        var b = y, w = b.stateNode, N = b.tag;
        if (N === ae && w !== null && (g = w, p !== null)) {
          var A = xl(y, p);
          A != null && v.push(tp(y, A, g));
        }
        if (u)
          break;
        y = y.return;
      }
      return v;
    }
    function gh(e, t) {
      for (var a = t + "Capture", i = [], u = e; u !== null; ) {
        var s = u, f = s.stateNode, p = s.tag;
        if (p === ae && f !== null) {
          var v = f, y = xl(u, a);
          y != null && i.unshift(tp(u, y, v));
          var g = xl(u, t);
          g != null && i.push(tp(u, g, v));
        }
        u = u.return;
      }
      return i;
    }
    function gf(e) {
      if (e === null)
        return null;
      do
        e = e.return;
      while (e && e.tag !== ae);
      return e || null;
    }
    function bT(e, t) {
      for (var a = e, i = t, u = 0, s = a; s; s = gf(s))
        u++;
      for (var f = 0, p = i; p; p = gf(p))
        f++;
      for (; u - f > 0; )
        a = gf(a), u--;
      for (; f - u > 0; )
        i = gf(i), f--;
      for (var v = u; v--; ) {
        if (a === i || i !== null && a === i.alternate)
          return a;
        a = gf(a), i = gf(i);
      }
      return null;
    }
    function DE(e, t, a, i, u) {
      for (var s = t._reactName, f = [], p = a; p !== null && p !== i; ) {
        var v = p, y = v.alternate, g = v.stateNode, b = v.tag;
        if (y !== null && y === i)
          break;
        if (b === ae && g !== null) {
          var w = g;
          if (u) {
            var N = xl(p, s);
            N != null && f.unshift(tp(p, N, w));
          } else if (!u) {
            var A = xl(p, s);
            A != null && f.push(tp(p, A, w));
          }
        }
        p = p.return;
      }
      f.length !== 0 && e.push({
        event: t,
        listeners: f
      });
    }
    function _T(e, t, a, i, u) {
      var s = i && u ? bT(i, u) : null;
      i !== null && DE(e, t, i, s, !1), u !== null && a !== null && DE(e, a, u, s, !0);
    }
    function kT(e, t) {
      return e + "__bubble";
    }
    var ja = !1, np = "dangerouslySetInnerHTML", Sh = "suppressContentEditableWarning", ko = "suppressHydrationWarning", OE = "autoFocus", Bs = "children", Is = "style", Eh = "__html", by, Ch, rp, LE, Rh, ME, NE;
    by = {
      // There are working polyfills for <dialog>. Let people use it.
      dialog: !0,
      // Electron ships a custom <webview> tag to display external web content in
      // an isolated frame and process.
      // This tag is not present in non Electron environments such as JSDom which
      // is often used for testing purposes.
      // @see https://electronjs.org/docs/api/webview-tag
      webview: !0
    }, Ch = function(e, t) {
      ud(e, t), pc(e, t), Rv(e, t, {
        registrationNameDependencies: nt,
        possibleRegistrationNames: ut
      });
    }, ME = On && !document.documentMode, rp = function(e, t, a) {
      if (!ja) {
        var i = Th(a), u = Th(t);
        u !== i && (ja = !0, S("Prop `%s` did not match. Server: %s Client: %s", e, JSON.stringify(u), JSON.stringify(i)));
      }
    }, LE = function(e) {
      if (!ja) {
        ja = !0;
        var t = [];
        e.forEach(function(a) {
          t.push(a);
        }), S("Extra attributes from the server: %s", t);
      }
    }, Rh = function(e, t) {
      t === !1 ? S("Expected `%s` listener to be a function, instead got `false`.\n\nIf you used to conditionally omit it with %s={condition && value}, pass %s={condition ? value : undefined} instead.", e, e, e) : S("Expected `%s` listener to be a function, instead got a value of `%s` type.", e, typeof t);
    }, NE = function(e, t) {
      var a = e.namespaceURI === Ii ? e.ownerDocument.createElement(e.tagName) : e.ownerDocument.createElementNS(e.namespaceURI, e.tagName);
      return a.innerHTML = t, a.innerHTML;
    };
    var DT = /\r\n?/g, OT = /\u0000|\uFFFD/g;
    function Th(e) {
      Kn(e);
      var t = typeof e == "string" ? e : "" + e;
      return t.replace(DT, `
`).replace(OT, "");
    }
    function wh(e, t, a, i) {
      var u = Th(t), s = Th(e);
      if (s !== u && (i && (ja || (ja = !0, S('Text content did not match. Server: "%s" Client: "%s"', s, u))), a && Re))
        throw new Error("Text content does not match server-rendered HTML.");
    }
    function zE(e) {
      return e.nodeType === $i ? e : e.ownerDocument;
    }
    function LT() {
    }
    function xh(e) {
      e.onclick = LT;
    }
    function MT(e, t, a, i, u) {
      for (var s in i)
        if (i.hasOwnProperty(s)) {
          var f = i[s];
          if (s === Is)
            f && Object.freeze(f), mv(t, f);
          else if (s === np) {
            var p = f ? f[Eh] : void 0;
            p != null && av(t, p);
          } else if (s === Bs)
            if (typeof f == "string") {
              var v = e !== "textarea" || f !== "";
              v && ao(t, f);
            } else typeof f == "number" && ao(t, "" + f);
          else s === Sh || s === ko || s === OE || (nt.hasOwnProperty(s) ? f != null && (typeof f != "function" && Rh(s, f), s === "onScroll" && Sn("scroll", t)) : f != null && br(t, s, f, u));
        }
    }
    function NT(e, t, a, i) {
      for (var u = 0; u < t.length; u += 2) {
        var s = t[u], f = t[u + 1];
        s === Is ? mv(e, f) : s === np ? av(e, f) : s === Bs ? ao(e, f) : br(e, s, f, i);
      }
    }
    function zT(e, t, a, i) {
      var u, s = zE(a), f, p = i;
      if (p === Ii && (p = ed(e)), p === Ii) {
        if (u = Tl(e, t), !u && e !== e.toLowerCase() && S("<%s /> is using incorrect casing. Use PascalCase for React components, or lowercase for HTML elements.", e), e === "script") {
          var v = s.createElement("div");
          v.innerHTML = "<script><\/script>";
          var y = v.firstChild;
          f = v.removeChild(y);
        } else if (typeof t.is == "string")
          f = s.createElement(e, {
            is: t.is
          });
        else if (f = s.createElement(e), e === "select") {
          var g = f;
          t.multiple ? g.multiple = !0 : t.size && (g.size = t.size);
        }
      } else
        f = s.createElementNS(p, e);
      return p === Ii && !u && Object.prototype.toString.call(f) === "[object HTMLUnknownElement]" && !xr.call(by, e) && (by[e] = !0, S("The tag <%s> is unrecognized in this browser. If you meant to render a React component, start its name with an uppercase letter.", e)), f;
    }
    function UT(e, t) {
      return zE(t).createTextNode(e);
    }
    function AT(e, t, a, i) {
      var u = Tl(t, a);
      Ch(t, a);
      var s;
      switch (t) {
        case "dialog":
          Sn("cancel", e), Sn("close", e), s = a;
          break;
        case "iframe":
        case "object":
        case "embed":
          Sn("load", e), s = a;
          break;
        case "video":
        case "audio":
          for (var f = 0; f < Jd.length; f++)
            Sn(Jd[f], e);
          s = a;
          break;
        case "source":
          Sn("error", e), s = a;
          break;
        case "img":
        case "image":
        case "link":
          Sn("error", e), Sn("load", e), s = a;
          break;
        case "details":
          Sn("toggle", e), s = a;
          break;
        case "input":
          ei(e, a), s = ro(e, a), Sn("invalid", e);
          break;
        case "option":
          bt(e, a), s = a;
          break;
        case "select":
          ou(e, a), s = qo(e, a), Sn("invalid", e);
          break;
        case "textarea":
          Xf(e, a), s = qf(e, a), Sn("invalid", e);
          break;
        default:
          s = a;
      }
      switch (fc(t, s), MT(t, e, i, s, u), t) {
        case "input":
          Ja(e), z(e, a, !1);
          break;
        case "textarea":
          Ja(e), nv(e);
          break;
        case "option":
          rn(e, a);
          break;
        case "select":
          Gf(e, a);
          break;
        default:
          typeof s.onClick == "function" && xh(e);
          break;
      }
    }
    function jT(e, t, a, i, u) {
      Ch(t, i);
      var s = null, f, p;
      switch (t) {
        case "input":
          f = ro(e, a), p = ro(e, i), s = [];
          break;
        case "select":
          f = qo(e, a), p = qo(e, i), s = [];
          break;
        case "textarea":
          f = qf(e, a), p = qf(e, i), s = [];
          break;
        default:
          f = a, p = i, typeof f.onClick != "function" && typeof p.onClick == "function" && xh(e);
          break;
      }
      fc(t, p);
      var v, y, g = null;
      for (v in f)
        if (!(p.hasOwnProperty(v) || !f.hasOwnProperty(v) || f[v] == null))
          if (v === Is) {
            var b = f[v];
            for (y in b)
              b.hasOwnProperty(y) && (g || (g = {}), g[y] = "");
          } else v === np || v === Bs || v === Sh || v === ko || v === OE || (nt.hasOwnProperty(v) ? s || (s = []) : (s = s || []).push(v, null));
      for (v in p) {
        var w = p[v], N = f != null ? f[v] : void 0;
        if (!(!p.hasOwnProperty(v) || w === N || w == null && N == null))
          if (v === Is)
            if (w && Object.freeze(w), N) {
              for (y in N)
                N.hasOwnProperty(y) && (!w || !w.hasOwnProperty(y)) && (g || (g = {}), g[y] = "");
              for (y in w)
                w.hasOwnProperty(y) && N[y] !== w[y] && (g || (g = {}), g[y] = w[y]);
            } else
              g || (s || (s = []), s.push(v, g)), g = w;
          else if (v === np) {
            var A = w ? w[Eh] : void 0, H = N ? N[Eh] : void 0;
            A != null && H !== A && (s = s || []).push(v, A);
          } else v === Bs ? (typeof w == "string" || typeof w == "number") && (s = s || []).push(v, "" + w) : v === Sh || v === ko || (nt.hasOwnProperty(v) ? (w != null && (typeof w != "function" && Rh(v, w), v === "onScroll" && Sn("scroll", e)), !s && N !== w && (s = [])) : (s = s || []).push(v, w));
      }
      return g && (Jm(g, p[Is]), (s = s || []).push(Is, g)), s;
    }
    function FT(e, t, a, i, u) {
      a === "input" && u.type === "radio" && u.name != null && h(e, u);
      var s = Tl(a, i), f = Tl(a, u);
      switch (NT(e, t, s, f), a) {
        case "input":
          C(e, u);
          break;
        case "textarea":
          tv(e, u);
          break;
        case "select":
          oc(e, u);
          break;
      }
    }
    function HT(e) {
      {
        var t = e.toLowerCase();
        return ts.hasOwnProperty(t) && ts[t] || null;
      }
    }
    function PT(e, t, a, i, u, s, f) {
      var p, v;
      switch (p = Tl(t, a), Ch(t, a), t) {
        case "dialog":
          Sn("cancel", e), Sn("close", e);
          break;
        case "iframe":
        case "object":
        case "embed":
          Sn("load", e);
          break;
        case "video":
        case "audio":
          for (var y = 0; y < Jd.length; y++)
            Sn(Jd[y], e);
          break;
        case "source":
          Sn("error", e);
          break;
        case "img":
        case "image":
        case "link":
          Sn("error", e), Sn("load", e);
          break;
        case "details":
          Sn("toggle", e);
          break;
        case "input":
          ei(e, a), Sn("invalid", e);
          break;
        case "option":
          bt(e, a);
          break;
        case "select":
          ou(e, a), Sn("invalid", e);
          break;
        case "textarea":
          Xf(e, a), Sn("invalid", e);
          break;
      }
      fc(t, a);
      {
        v = /* @__PURE__ */ new Set();
        for (var g = e.attributes, b = 0; b < g.length; b++) {
          var w = g[b].name.toLowerCase();
          switch (w) {
            case "value":
              break;
            case "checked":
              break;
            case "selected":
              break;
            default:
              v.add(g[b].name);
          }
        }
      }
      var N = null;
      for (var A in a)
        if (a.hasOwnProperty(A)) {
          var H = a[A];
          if (A === Bs)
            typeof H == "string" ? e.textContent !== H && (a[ko] !== !0 && wh(e.textContent, H, s, f), N = [Bs, H]) : typeof H == "number" && e.textContent !== "" + H && (a[ko] !== !0 && wh(e.textContent, H, s, f), N = [Bs, "" + H]);
          else if (nt.hasOwnProperty(A))
            H != null && (typeof H != "function" && Rh(A, H), A === "onScroll" && Sn("scroll", e));
          else if (f && // Convince Flow we've calculated it (it's DEV-only in this method.)
          typeof p == "boolean") {
            var ue = void 0, ze = tn(A);
            if (a[ko] !== !0) {
              if (!(A === Sh || A === ko || // Controlled attributes are not validated
              // TODO: Only ignore them on controlled tags.
              A === "value" || A === "checked" || A === "selected")) {
                if (A === np) {
                  var be = e.innerHTML, wt = H ? H[Eh] : void 0;
                  if (wt != null) {
                    var yt = NE(e, wt);
                    yt !== be && rp(A, be, yt);
                  }
                } else if (A === Is) {
                  if (v.delete(A), ME) {
                    var O = Xm(H);
                    ue = e.getAttribute("style"), O !== ue && rp(A, ue, O);
                  }
                } else if (p && !_)
                  v.delete(A.toLowerCase()), ue = tu(e, A, H), H !== ue && rp(A, ue, H);
                else if (!vn(A, ze, p) && !qn(A, H, ze, p)) {
                  var P = !1;
                  if (ze !== null)
                    v.delete(ze.attributeName), ue = vl(e, A, H, ze);
                  else {
                    var L = i;
                    if (L === Ii && (L = ed(t)), L === Ii)
                      v.delete(A.toLowerCase());
                    else {
                      var q = HT(A);
                      q !== null && q !== A && (P = !0, v.delete(q)), v.delete(A);
                    }
                    ue = tu(e, A, H);
                  }
                  var pe = _;
                  !pe && H !== ue && !P && rp(A, ue, H);
                }
              }
            }
          }
        }
      switch (f && // $FlowFixMe - Should be inferred as not undefined.
      v.size > 0 && a[ko] !== !0 && LE(v), t) {
        case "input":
          Ja(e), z(e, a, !0);
          break;
        case "textarea":
          Ja(e), nv(e);
          break;
        case "select":
        case "option":
          break;
        default:
          typeof a.onClick == "function" && xh(e);
          break;
      }
      return N;
    }
    function VT(e, t, a) {
      var i = e.nodeValue !== t;
      return i;
    }
    function _y(e, t) {
      {
        if (ja)
          return;
        ja = !0, S("Did not expect server HTML to contain a <%s> in <%s>.", t.nodeName.toLowerCase(), e.nodeName.toLowerCase());
      }
    }
    function ky(e, t) {
      {
        if (ja)
          return;
        ja = !0, S('Did not expect server HTML to contain the text node "%s" in <%s>.', t.nodeValue, e.nodeName.toLowerCase());
      }
    }
    function Dy(e, t, a) {
      {
        if (ja)
          return;
        ja = !0, S("Expected server HTML to contain a matching <%s> in <%s>.", t, e.nodeName.toLowerCase());
      }
    }
    function Oy(e, t) {
      {
        if (t === "" || ja)
          return;
        ja = !0, S('Expected server HTML to contain a matching text node for "%s" in <%s>.', t, e.nodeName.toLowerCase());
      }
    }
    function BT(e, t, a) {
      switch (t) {
        case "input":
          F(e, a);
          return;
        case "textarea":
          Wm(e, a);
          return;
        case "select":
          Kf(e, a);
          return;
      }
    }
    var ap = function() {
    }, ip = function() {
    };
    {
      var IT = ["address", "applet", "area", "article", "aside", "base", "basefont", "bgsound", "blockquote", "body", "br", "button", "caption", "center", "col", "colgroup", "dd", "details", "dir", "div", "dl", "dt", "embed", "fieldset", "figcaption", "figure", "footer", "form", "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "iframe", "img", "input", "isindex", "li", "link", "listing", "main", "marquee", "menu", "menuitem", "meta", "nav", "noembed", "noframes", "noscript", "object", "ol", "p", "param", "plaintext", "pre", "script", "section", "select", "source", "style", "summary", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "title", "tr", "track", "ul", "wbr", "xmp"], UE = [
        "applet",
        "caption",
        "html",
        "table",
        "td",
        "th",
        "marquee",
        "object",
        "template",
        // https://html.spec.whatwg.org/multipage/syntax.html#html-integration-point
        // TODO: Distinguish by namespace here -- for <title>, including it here
        // errs on the side of fewer warnings
        "foreignObject",
        "desc",
        "title"
      ], YT = UE.concat(["button"]), $T = ["dd", "dt", "li", "option", "optgroup", "p", "rp", "rt"], AE = {
        current: null,
        formTag: null,
        aTagInScope: null,
        buttonTagInScope: null,
        nobrTagInScope: null,
        pTagInButtonScope: null,
        listItemTagAutoclosing: null,
        dlItemTagAutoclosing: null
      };
      ip = function(e, t) {
        var a = rt({}, e || AE), i = {
          tag: t
        };
        return UE.indexOf(t) !== -1 && (a.aTagInScope = null, a.buttonTagInScope = null, a.nobrTagInScope = null), YT.indexOf(t) !== -1 && (a.pTagInButtonScope = null), IT.indexOf(t) !== -1 && t !== "address" && t !== "div" && t !== "p" && (a.listItemTagAutoclosing = null, a.dlItemTagAutoclosing = null), a.current = i, t === "form" && (a.formTag = i), t === "a" && (a.aTagInScope = i), t === "button" && (a.buttonTagInScope = i), t === "nobr" && (a.nobrTagInScope = i), t === "p" && (a.pTagInButtonScope = i), t === "li" && (a.listItemTagAutoclosing = i), (t === "dd" || t === "dt") && (a.dlItemTagAutoclosing = i), a;
      };
      var QT = function(e, t) {
        switch (t) {
          case "select":
            return e === "option" || e === "optgroup" || e === "#text";
          case "optgroup":
            return e === "option" || e === "#text";
          case "option":
            return e === "#text";
          case "tr":
            return e === "th" || e === "td" || e === "style" || e === "script" || e === "template";
          case "tbody":
          case "thead":
          case "tfoot":
            return e === "tr" || e === "style" || e === "script" || e === "template";
          case "colgroup":
            return e === "col" || e === "template";
          case "table":
            return e === "caption" || e === "colgroup" || e === "tbody" || e === "tfoot" || e === "thead" || e === "style" || e === "script" || e === "template";
          case "head":
            return e === "base" || e === "basefont" || e === "bgsound" || e === "link" || e === "meta" || e === "title" || e === "noscript" || e === "noframes" || e === "style" || e === "script" || e === "template";
          case "html":
            return e === "head" || e === "body" || e === "frameset";
          case "frameset":
            return e === "frame";
          case "#document":
            return e === "html";
        }
        switch (e) {
          case "h1":
          case "h2":
          case "h3":
          case "h4":
          case "h5":
          case "h6":
            return t !== "h1" && t !== "h2" && t !== "h3" && t !== "h4" && t !== "h5" && t !== "h6";
          case "rp":
          case "rt":
            return $T.indexOf(t) === -1;
          case "body":
          case "caption":
          case "col":
          case "colgroup":
          case "frameset":
          case "frame":
          case "head":
          case "html":
          case "tbody":
          case "td":
          case "tfoot":
          case "th":
          case "thead":
          case "tr":
            return t == null;
        }
        return !0;
      }, WT = function(e, t) {
        switch (e) {
          case "address":
          case "article":
          case "aside":
          case "blockquote":
          case "center":
          case "details":
          case "dialog":
          case "dir":
          case "div":
          case "dl":
          case "fieldset":
          case "figcaption":
          case "figure":
          case "footer":
          case "header":
          case "hgroup":
          case "main":
          case "menu":
          case "nav":
          case "ol":
          case "p":
          case "section":
          case "summary":
          case "ul":
          case "pre":
          case "listing":
          case "table":
          case "hr":
          case "xmp":
          case "h1":
          case "h2":
          case "h3":
          case "h4":
          case "h5":
          case "h6":
            return t.pTagInButtonScope;
          case "form":
            return t.formTag || t.pTagInButtonScope;
          case "li":
            return t.listItemTagAutoclosing;
          case "dd":
          case "dt":
            return t.dlItemTagAutoclosing;
          case "button":
            return t.buttonTagInScope;
          case "a":
            return t.aTagInScope;
          case "nobr":
            return t.nobrTagInScope;
        }
        return null;
      }, jE = {};
      ap = function(e, t, a) {
        a = a || AE;
        var i = a.current, u = i && i.tag;
        t != null && (e != null && S("validateDOMNesting: when childText is passed, childTag should be null"), e = "#text");
        var s = QT(e, u) ? null : i, f = s ? null : WT(e, a), p = s || f;
        if (p) {
          var v = p.tag, y = !!s + "|" + e + "|" + v;
          if (!jE[y]) {
            jE[y] = !0;
            var g = e, b = "";
            if (e === "#text" ? /\S/.test(t) ? g = "Text nodes" : (g = "Whitespace text nodes", b = " Make sure you don't have any extra whitespace between tags on each line of your source code.") : g = "<" + e + ">", s) {
              var w = "";
              v === "table" && e === "tr" && (w += " Add a <tbody>, <thead> or <tfoot> to your code to match the DOM tree generated by the browser."), S("validateDOMNesting(...): %s cannot appear as a child of <%s>.%s%s", g, v, b, w);
            } else
              S("validateDOMNesting(...): %s cannot appear as a descendant of <%s>.", g, v);
          }
        }
      };
    }
    var bh = "suppressHydrationWarning", _h = "$", kh = "/$", lp = "$?", up = "$!", GT = "style", Ly = null, My = null;
    function KT(e) {
      var t, a, i = e.nodeType;
      switch (i) {
        case $i:
        case nd: {
          t = i === $i ? "#document" : "#fragment";
          var u = e.documentElement;
          a = u ? u.namespaceURI : td(null, "");
          break;
        }
        default: {
          var s = i === Mn ? e.parentNode : e, f = s.namespaceURI || null;
          t = s.tagName, a = td(f, t);
          break;
        }
      }
      {
        var p = t.toLowerCase(), v = ip(null, p);
        return {
          namespace: a,
          ancestorInfo: v
        };
      }
    }
    function qT(e, t, a) {
      {
        var i = e, u = td(i.namespace, t), s = ip(i.ancestorInfo, t);
        return {
          namespace: u,
          ancestorInfo: s
        };
      }
    }
    function Sk(e) {
      return e;
    }
    function XT(e) {
      Ly = Fn(), My = fT();
      var t = null;
      return Wn(!1), t;
    }
    function ZT(e) {
      dT(My), Wn(Ly), Ly = null, My = null;
    }
    function JT(e, t, a, i, u) {
      var s;
      {
        var f = i;
        if (ap(e, null, f.ancestorInfo), typeof t.children == "string" || typeof t.children == "number") {
          var p = "" + t.children, v = ip(f.ancestorInfo, e);
          ap(null, p, v);
        }
        s = f.namespace;
      }
      var y = zT(e, t, a, s);
      return cp(u, y), Py(y, t), y;
    }
    function ew(e, t) {
      e.appendChild(t);
    }
    function tw(e, t, a, i, u) {
      switch (AT(e, t, a, i), t) {
        case "button":
        case "input":
        case "select":
        case "textarea":
          return !!a.autoFocus;
        case "img":
          return !0;
        default:
          return !1;
      }
    }
    function nw(e, t, a, i, u, s) {
      {
        var f = s;
        if (typeof i.children != typeof a.children && (typeof i.children == "string" || typeof i.children == "number")) {
          var p = "" + i.children, v = ip(f.ancestorInfo, t);
          ap(null, p, v);
        }
      }
      return jT(e, t, a, i);
    }
    function Ny(e, t) {
      return e === "textarea" || e === "noscript" || typeof t.children == "string" || typeof t.children == "number" || typeof t.dangerouslySetInnerHTML == "object" && t.dangerouslySetInnerHTML !== null && t.dangerouslySetInnerHTML.__html != null;
    }
    function rw(e, t, a, i) {
      {
        var u = a;
        ap(null, e, u.ancestorInfo);
      }
      var s = UT(e, t);
      return cp(i, s), s;
    }
    function aw() {
      var e = window.event;
      return e === void 0 ? Na : af(e.type);
    }
    var zy = typeof setTimeout == "function" ? setTimeout : void 0, iw = typeof clearTimeout == "function" ? clearTimeout : void 0, Uy = -1, FE = typeof Promise == "function" ? Promise : void 0, lw = typeof queueMicrotask == "function" ? queueMicrotask : typeof FE < "u" ? function(e) {
      return FE.resolve(null).then(e).catch(uw);
    } : zy;
    function uw(e) {
      setTimeout(function() {
        throw e;
      });
    }
    function ow(e, t, a, i) {
      switch (t) {
        case "button":
        case "input":
        case "select":
        case "textarea":
          a.autoFocus && e.focus();
          return;
        case "img": {
          a.src && (e.src = a.src);
          return;
        }
      }
    }
    function sw(e, t, a, i, u, s) {
      FT(e, t, a, i, u), Py(e, u);
    }
    function HE(e) {
      ao(e, "");
    }
    function cw(e, t, a) {
      e.nodeValue = a;
    }
    function fw(e, t) {
      e.appendChild(t);
    }
    function dw(e, t) {
      var a;
      e.nodeType === Mn ? (a = e.parentNode, a.insertBefore(t, e)) : (a = e, a.appendChild(t));
      var i = e._reactRootContainer;
      i == null && a.onclick === null && xh(a);
    }
    function pw(e, t, a) {
      e.insertBefore(t, a);
    }
    function vw(e, t, a) {
      e.nodeType === Mn ? e.parentNode.insertBefore(t, a) : e.insertBefore(t, a);
    }
    function hw(e, t) {
      e.removeChild(t);
    }
    function mw(e, t) {
      e.nodeType === Mn ? e.parentNode.removeChild(t) : e.removeChild(t);
    }
    function Ay(e, t) {
      var a = t, i = 0;
      do {
        var u = a.nextSibling;
        if (e.removeChild(a), u && u.nodeType === Mn) {
          var s = u.data;
          if (s === kh)
            if (i === 0) {
              e.removeChild(u), Du(t);
              return;
            } else
              i--;
          else (s === _h || s === lp || s === up) && i++;
        }
        a = u;
      } while (a);
      Du(t);
    }
    function yw(e, t) {
      e.nodeType === Mn ? Ay(e.parentNode, t) : e.nodeType === Qr && Ay(e, t), Du(e);
    }
    function gw(e) {
      e = e;
      var t = e.style;
      typeof t.setProperty == "function" ? t.setProperty("display", "none", "important") : t.display = "none";
    }
    function Sw(e) {
      e.nodeValue = "";
    }
    function Ew(e, t) {
      e = e;
      var a = t[GT], i = a != null && a.hasOwnProperty("display") ? a.display : null;
      e.style.display = cc("display", i);
    }
    function Cw(e, t) {
      e.nodeValue = t;
    }
    function Rw(e) {
      e.nodeType === Qr ? e.textContent = "" : e.nodeType === $i && e.documentElement && e.removeChild(e.documentElement);
    }
    function Tw(e, t, a) {
      return e.nodeType !== Qr || t.toLowerCase() !== e.nodeName.toLowerCase() ? null : e;
    }
    function ww(e, t) {
      return t === "" || e.nodeType !== Yi ? null : e;
    }
    function xw(e) {
      return e.nodeType !== Mn ? null : e;
    }
    function PE(e) {
      return e.data === lp;
    }
    function jy(e) {
      return e.data === up;
    }
    function bw(e) {
      var t = e.nextSibling && e.nextSibling.dataset, a, i, u;
      return t && (a = t.dgst, i = t.msg, u = t.stck), {
        message: i,
        digest: a,
        stack: u
      };
    }
    function _w(e, t) {
      e._reactRetry = t;
    }
    function Dh(e) {
      for (; e != null; e = e.nextSibling) {
        var t = e.nodeType;
        if (t === Qr || t === Yi)
          break;
        if (t === Mn) {
          var a = e.data;
          if (a === _h || a === up || a === lp)
            break;
          if (a === kh)
            return null;
        }
      }
      return e;
    }
    function op(e) {
      return Dh(e.nextSibling);
    }
    function kw(e) {
      return Dh(e.firstChild);
    }
    function Dw(e) {
      return Dh(e.firstChild);
    }
    function Ow(e) {
      return Dh(e.nextSibling);
    }
    function Lw(e, t, a, i, u, s, f) {
      cp(s, e), Py(e, a);
      var p;
      {
        var v = u;
        p = v.namespace;
      }
      var y = (s.mode & vt) !== Oe;
      return PT(e, t, a, p, i, y, f);
    }
    function Mw(e, t, a, i) {
      return cp(a, e), a.mode & vt, VT(e, t);
    }
    function Nw(e, t) {
      cp(t, e);
    }
    function zw(e) {
      for (var t = e.nextSibling, a = 0; t; ) {
        if (t.nodeType === Mn) {
          var i = t.data;
          if (i === kh) {
            if (a === 0)
              return op(t);
            a--;
          } else (i === _h || i === up || i === lp) && a++;
        }
        t = t.nextSibling;
      }
      return null;
    }
    function VE(e) {
      for (var t = e.previousSibling, a = 0; t; ) {
        if (t.nodeType === Mn) {
          var i = t.data;
          if (i === _h || i === up || i === lp) {
            if (a === 0)
              return t;
            a--;
          } else i === kh && a++;
        }
        t = t.previousSibling;
      }
      return null;
    }
    function Uw(e) {
      Du(e);
    }
    function Aw(e) {
      Du(e);
    }
    function jw(e) {
      return e !== "head" && e !== "body";
    }
    function Fw(e, t, a, i) {
      var u = !0;
      wh(t.nodeValue, a, i, u);
    }
    function Hw(e, t, a, i, u, s) {
      if (t[bh] !== !0) {
        var f = !0;
        wh(i.nodeValue, u, s, f);
      }
    }
    function Pw(e, t) {
      t.nodeType === Qr ? _y(e, t) : t.nodeType === Mn || ky(e, t);
    }
    function Vw(e, t) {
      {
        var a = e.parentNode;
        a !== null && (t.nodeType === Qr ? _y(a, t) : t.nodeType === Mn || ky(a, t));
      }
    }
    function Bw(e, t, a, i, u) {
      (u || t[bh] !== !0) && (i.nodeType === Qr ? _y(a, i) : i.nodeType === Mn || ky(a, i));
    }
    function Iw(e, t, a) {
      Dy(e, t);
    }
    function Yw(e, t) {
      Oy(e, t);
    }
    function $w(e, t, a) {
      {
        var i = e.parentNode;
        i !== null && Dy(i, t);
      }
    }
    function Qw(e, t) {
      {
        var a = e.parentNode;
        a !== null && Oy(a, t);
      }
    }
    function Ww(e, t, a, i, u, s) {
      (s || t[bh] !== !0) && Dy(a, i);
    }
    function Gw(e, t, a, i, u) {
      (u || t[bh] !== !0) && Oy(a, i);
    }
    function Kw(e) {
      S("An error occurred during hydration. The server HTML was replaced with client content in <%s>.", e.nodeName.toLowerCase());
    }
    function qw(e) {
      ep(e);
    }
    var Sf = Math.random().toString(36).slice(2), Ef = "__reactFiber$" + Sf, Fy = "__reactProps$" + Sf, sp = "__reactContainer$" + Sf, Hy = "__reactEvents$" + Sf, Xw = "__reactListeners$" + Sf, Zw = "__reactHandles$" + Sf;
    function Jw(e) {
      delete e[Ef], delete e[Fy], delete e[Hy], delete e[Xw], delete e[Zw];
    }
    function cp(e, t) {
      t[Ef] = e;
    }
    function Oh(e, t) {
      t[sp] = e;
    }
    function BE(e) {
      e[sp] = null;
    }
    function fp(e) {
      return !!e[sp];
    }
    function Ys(e) {
      var t = e[Ef];
      if (t)
        return t;
      for (var a = e.parentNode; a; ) {
        if (t = a[sp] || a[Ef], t) {
          var i = t.alternate;
          if (t.child !== null || i !== null && i.child !== null)
            for (var u = VE(e); u !== null; ) {
              var s = u[Ef];
              if (s)
                return s;
              u = VE(u);
            }
          return t;
        }
        e = a, a = e.parentNode;
      }
      return null;
    }
    function Do(e) {
      var t = e[Ef] || e[sp];
      return t && (t.tag === ae || t.tag === Ve || t.tag === ke || t.tag === J) ? t : null;
    }
    function Cf(e) {
      if (e.tag === ae || e.tag === Ve)
        return e.stateNode;
      throw new Error("getNodeFromInstance: Invalid argument.");
    }
    function Lh(e) {
      return e[Fy] || null;
    }
    function Py(e, t) {
      e[Fy] = t;
    }
    function ex(e) {
      var t = e[Hy];
      return t === void 0 && (t = e[Hy] = /* @__PURE__ */ new Set()), t;
    }
    var IE = {}, YE = k.ReactDebugCurrentFrame;
    function Mh(e) {
      if (e) {
        var t = e._owner, a = Pi(e.type, e._source, t ? t.type : null);
        YE.setExtraStackFrame(a);
      } else
        YE.setExtraStackFrame(null);
    }
    function nl(e, t, a, i, u) {
      {
        var s = Function.call.bind(xr);
        for (var f in e)
          if (s(e, f)) {
            var p = void 0;
            try {
              if (typeof e[f] != "function") {
                var v = Error((i || "React class") + ": " + a + " type `" + f + "` is invalid; it must be a function, usually from the `prop-types` package, but received `" + typeof e[f] + "`.This often happens because of typos such as `PropTypes.function` instead of `PropTypes.func`.");
                throw v.name = "Invariant Violation", v;
              }
              p = e[f](t, f, i, a, null, "SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED");
            } catch (y) {
              p = y;
            }
            p && !(p instanceof Error) && (Mh(u), S("%s: type specification of %s `%s` is invalid; the type checker function must return `null` or an `Error` but returned a %s. You may have forgotten to pass an argument to the type checker creator (arrayOf, instanceOf, objectOf, oneOf, oneOfType, and shape all require an argument).", i || "React class", a, f, typeof p), Mh(null)), p instanceof Error && !(p.message in IE) && (IE[p.message] = !0, Mh(u), S("Failed %s type: %s", a, p.message), Mh(null));
          }
      }
    }
    var Vy = [], Nh;
    Nh = [];
    var Uu = -1;
    function Oo(e) {
      return {
        current: e
      };
    }
    function ra(e, t) {
      if (Uu < 0) {
        S("Unexpected pop.");
        return;
      }
      t !== Nh[Uu] && S("Unexpected Fiber popped."), e.current = Vy[Uu], Vy[Uu] = null, Nh[Uu] = null, Uu--;
    }
    function aa(e, t, a) {
      Uu++, Vy[Uu] = e.current, Nh[Uu] = a, e.current = t;
    }
    var By;
    By = {};
    var ui = {};
    Object.freeze(ui);
    var Au = Oo(ui), Il = Oo(!1), Iy = ui;
    function Rf(e, t, a) {
      return a && Yl(t) ? Iy : Au.current;
    }
    function $E(e, t, a) {
      {
        var i = e.stateNode;
        i.__reactInternalMemoizedUnmaskedChildContext = t, i.__reactInternalMemoizedMaskedChildContext = a;
      }
    }
    function Tf(e, t) {
      {
        var a = e.type, i = a.contextTypes;
        if (!i)
          return ui;
        var u = e.stateNode;
        if (u && u.__reactInternalMemoizedUnmaskedChildContext === t)
          return u.__reactInternalMemoizedMaskedChildContext;
        var s = {};
        for (var f in i)
          s[f] = t[f];
        {
          var p = We(e) || "Unknown";
          nl(i, s, "context", p);
        }
        return u && $E(e, t, s), s;
      }
    }
    function zh() {
      return Il.current;
    }
    function Yl(e) {
      {
        var t = e.childContextTypes;
        return t != null;
      }
    }
    function Uh(e) {
      ra(Il, e), ra(Au, e);
    }
    function Yy(e) {
      ra(Il, e), ra(Au, e);
    }
    function QE(e, t, a) {
      {
        if (Au.current !== ui)
          throw new Error("Unexpected context found on stack. This error is likely caused by a bug in React. Please file an issue.");
        aa(Au, t, e), aa(Il, a, e);
      }
    }
    function WE(e, t, a) {
      {
        var i = e.stateNode, u = t.childContextTypes;
        if (typeof i.getChildContext != "function") {
          {
            var s = We(e) || "Unknown";
            By[s] || (By[s] = !0, S("%s.childContextTypes is specified but there is no getChildContext() method on the instance. You can either define getChildContext() on %s or remove childContextTypes from it.", s, s));
          }
          return a;
        }
        var f = i.getChildContext();
        for (var p in f)
          if (!(p in u))
            throw new Error((We(e) || "Unknown") + '.getChildContext(): key "' + p + '" is not defined in childContextTypes.');
        {
          var v = We(e) || "Unknown";
          nl(u, f, "child context", v);
        }
        return rt({}, a, f);
      }
    }
    function Ah(e) {
      {
        var t = e.stateNode, a = t && t.__reactInternalMemoizedMergedChildContext || ui;
        return Iy = Au.current, aa(Au, a, e), aa(Il, Il.current, e), !0;
      }
    }
    function GE(e, t, a) {
      {
        var i = e.stateNode;
        if (!i)
          throw new Error("Expected to have an instance by this point. This error is likely caused by a bug in React. Please file an issue.");
        if (a) {
          var u = WE(e, t, Iy);
          i.__reactInternalMemoizedMergedChildContext = u, ra(Il, e), ra(Au, e), aa(Au, u, e), aa(Il, a, e);
        } else
          ra(Il, e), aa(Il, a, e);
      }
    }
    function tx(e) {
      {
        if (!hu(e) || e.tag !== ce)
          throw new Error("Expected subtree parent to be a mounted class component. This error is likely caused by a bug in React. Please file an issue.");
        var t = e;
        do {
          switch (t.tag) {
            case J:
              return t.stateNode.context;
            case ce: {
              var a = t.type;
              if (Yl(a))
                return t.stateNode.__reactInternalMemoizedMergedChildContext;
              break;
            }
          }
          t = t.return;
        } while (t !== null);
        throw new Error("Found unexpected detached subtree parent. This error is likely caused by a bug in React. Please file an issue.");
      }
    }
    var Lo = 0, jh = 1, ju = null, $y = !1, Qy = !1;
    function KE(e) {
      ju === null ? ju = [e] : ju.push(e);
    }
    function nx(e) {
      $y = !0, KE(e);
    }
    function qE() {
      $y && Mo();
    }
    function Mo() {
      if (!Qy && ju !== null) {
        Qy = !0;
        var e = 0, t = Ua();
        try {
          var a = !0, i = ju;
          for (jn(Lr); e < i.length; e++) {
            var u = i[e];
            do
              u = u(a);
            while (u !== null);
          }
          ju = null, $y = !1;
        } catch (s) {
          throw ju !== null && (ju = ju.slice(e + 1)), vd(ss, Mo), s;
        } finally {
          jn(t), Qy = !1;
        }
      }
      return null;
    }
    var wf = [], xf = 0, Fh = null, Hh = 0, Mi = [], Ni = 0, $s = null, Fu = 1, Hu = "";
    function rx(e) {
      return Ws(), (e.flags & Ri) !== De;
    }
    function ax(e) {
      return Ws(), Hh;
    }
    function ix() {
      var e = Hu, t = Fu, a = t & ~lx(t);
      return a.toString(32) + e;
    }
    function Qs(e, t) {
      Ws(), wf[xf++] = Hh, wf[xf++] = Fh, Fh = e, Hh = t;
    }
    function XE(e, t, a) {
      Ws(), Mi[Ni++] = Fu, Mi[Ni++] = Hu, Mi[Ni++] = $s, $s = e;
      var i = Fu, u = Hu, s = Ph(i) - 1, f = i & ~(1 << s), p = a + 1, v = Ph(t) + s;
      if (v > 30) {
        var y = s - s % 5, g = (1 << y) - 1, b = (f & g).toString(32), w = f >> y, N = s - y, A = Ph(t) + N, H = p << N, ue = H | w, ze = b + u;
        Fu = 1 << A | ue, Hu = ze;
      } else {
        var be = p << s, wt = be | f, yt = u;
        Fu = 1 << v | wt, Hu = yt;
      }
    }
    function Wy(e) {
      Ws();
      var t = e.return;
      if (t !== null) {
        var a = 1, i = 0;
        Qs(e, a), XE(e, a, i);
      }
    }
    function Ph(e) {
      return 32 - Un(e);
    }
    function lx(e) {
      return 1 << Ph(e) - 1;
    }
    function Gy(e) {
      for (; e === Fh; )
        Fh = wf[--xf], wf[xf] = null, Hh = wf[--xf], wf[xf] = null;
      for (; e === $s; )
        $s = Mi[--Ni], Mi[Ni] = null, Hu = Mi[--Ni], Mi[Ni] = null, Fu = Mi[--Ni], Mi[Ni] = null;
    }
    function ux() {
      return Ws(), $s !== null ? {
        id: Fu,
        overflow: Hu
      } : null;
    }
    function ox(e, t) {
      Ws(), Mi[Ni++] = Fu, Mi[Ni++] = Hu, Mi[Ni++] = $s, Fu = t.id, Hu = t.overflow, $s = e;
    }
    function Ws() {
      Ar() || S("Expected to be hydrating. This is a bug in React. Please file an issue.");
    }
    var Ur = null, zi = null, rl = !1, Gs = !1, No = null;
    function sx() {
      rl && S("We should not be hydrating here. This is a bug in React. Please file a bug.");
    }
    function ZE() {
      Gs = !0;
    }
    function cx() {
      return Gs;
    }
    function fx(e) {
      var t = e.stateNode.containerInfo;
      return zi = Dw(t), Ur = e, rl = !0, No = null, Gs = !1, !0;
    }
    function dx(e, t, a) {
      return zi = Ow(t), Ur = e, rl = !0, No = null, Gs = !1, a !== null && ox(e, a), !0;
    }
    function JE(e, t) {
      switch (e.tag) {
        case J: {
          Pw(e.stateNode.containerInfo, t);
          break;
        }
        case ae: {
          var a = (e.mode & vt) !== Oe;
          Bw(
            e.type,
            e.memoizedProps,
            e.stateNode,
            t,
            // TODO: Delete this argument when we remove the legacy root API.
            a
          );
          break;
        }
        case ke: {
          var i = e.memoizedState;
          i.dehydrated !== null && Vw(i.dehydrated, t);
          break;
        }
      }
    }
    function eC(e, t) {
      JE(e, t);
      var a = m_();
      a.stateNode = t, a.return = e;
      var i = e.deletions;
      i === null ? (e.deletions = [a], e.flags |= ka) : i.push(a);
    }
    function Ky(e, t) {
      {
        if (Gs)
          return;
        switch (e.tag) {
          case J: {
            var a = e.stateNode.containerInfo;
            switch (t.tag) {
              case ae:
                var i = t.type;
                t.pendingProps, Iw(a, i);
                break;
              case Ve:
                var u = t.pendingProps;
                Yw(a, u);
                break;
            }
            break;
          }
          case ae: {
            var s = e.type, f = e.memoizedProps, p = e.stateNode;
            switch (t.tag) {
              case ae: {
                var v = t.type, y = t.pendingProps, g = (e.mode & vt) !== Oe;
                Ww(
                  s,
                  f,
                  p,
                  v,
                  y,
                  // TODO: Delete this argument when we remove the legacy root API.
                  g
                );
                break;
              }
              case Ve: {
                var b = t.pendingProps, w = (e.mode & vt) !== Oe;
                Gw(
                  s,
                  f,
                  p,
                  b,
                  // TODO: Delete this argument when we remove the legacy root API.
                  w
                );
                break;
              }
            }
            break;
          }
          case ke: {
            var N = e.memoizedState, A = N.dehydrated;
            if (A !== null) switch (t.tag) {
              case ae:
                var H = t.type;
                t.pendingProps, $w(A, H);
                break;
              case Ve:
                var ue = t.pendingProps;
                Qw(A, ue);
                break;
            }
            break;
          }
          default:
            return;
        }
      }
    }
    function tC(e, t) {
      t.flags = t.flags & ~Gr | mn, Ky(e, t);
    }
    function nC(e, t) {
      switch (e.tag) {
        case ae: {
          var a = e.type;
          e.pendingProps;
          var i = Tw(t, a);
          return i !== null ? (e.stateNode = i, Ur = e, zi = kw(i), !0) : !1;
        }
        case Ve: {
          var u = e.pendingProps, s = ww(t, u);
          return s !== null ? (e.stateNode = s, Ur = e, zi = null, !0) : !1;
        }
        case ke: {
          var f = xw(t);
          if (f !== null) {
            var p = {
              dehydrated: f,
              treeContext: ux(),
              retryLane: Zr
            };
            e.memoizedState = p;
            var v = y_(f);
            return v.return = e, e.child = v, Ur = e, zi = null, !0;
          }
          return !1;
        }
        default:
          return !1;
      }
    }
    function qy(e) {
      return (e.mode & vt) !== Oe && (e.flags & _e) === De;
    }
    function Xy(e) {
      throw new Error("Hydration failed because the initial UI does not match what was rendered on the server.");
    }
    function Zy(e) {
      if (rl) {
        var t = zi;
        if (!t) {
          qy(e) && (Ky(Ur, e), Xy()), tC(Ur, e), rl = !1, Ur = e;
          return;
        }
        var a = t;
        if (!nC(e, t)) {
          qy(e) && (Ky(Ur, e), Xy()), t = op(a);
          var i = Ur;
          if (!t || !nC(e, t)) {
            tC(Ur, e), rl = !1, Ur = e;
            return;
          }
          eC(i, a);
        }
      }
    }
    function px(e, t, a) {
      var i = e.stateNode, u = !Gs, s = Lw(i, e.type, e.memoizedProps, t, a, e, u);
      return e.updateQueue = s, s !== null;
    }
    function vx(e) {
      var t = e.stateNode, a = e.memoizedProps, i = Mw(t, a, e);
      if (i) {
        var u = Ur;
        if (u !== null)
          switch (u.tag) {
            case J: {
              var s = u.stateNode.containerInfo, f = (u.mode & vt) !== Oe;
              Fw(
                s,
                t,
                a,
                // TODO: Delete this argument when we remove the legacy root API.
                f
              );
              break;
            }
            case ae: {
              var p = u.type, v = u.memoizedProps, y = u.stateNode, g = (u.mode & vt) !== Oe;
              Hw(
                p,
                v,
                y,
                t,
                a,
                // TODO: Delete this argument when we remove the legacy root API.
                g
              );
              break;
            }
          }
      }
      return i;
    }
    function hx(e) {
      var t = e.memoizedState, a = t !== null ? t.dehydrated : null;
      if (!a)
        throw new Error("Expected to have a hydrated suspense instance. This error is likely caused by a bug in React. Please file an issue.");
      Nw(a, e);
    }
    function mx(e) {
      var t = e.memoizedState, a = t !== null ? t.dehydrated : null;
      if (!a)
        throw new Error("Expected to have a hydrated suspense instance. This error is likely caused by a bug in React. Please file an issue.");
      return zw(a);
    }
    function rC(e) {
      for (var t = e.return; t !== null && t.tag !== ae && t.tag !== J && t.tag !== ke; )
        t = t.return;
      Ur = t;
    }
    function Vh(e) {
      if (e !== Ur)
        return !1;
      if (!rl)
        return rC(e), rl = !0, !1;
      if (e.tag !== J && (e.tag !== ae || jw(e.type) && !Ny(e.type, e.memoizedProps))) {
        var t = zi;
        if (t)
          if (qy(e))
            aC(e), Xy();
          else
            for (; t; )
              eC(e, t), t = op(t);
      }
      return rC(e), e.tag === ke ? zi = mx(e) : zi = Ur ? op(e.stateNode) : null, !0;
    }
    function yx() {
      return rl && zi !== null;
    }
    function aC(e) {
      for (var t = zi; t; )
        JE(e, t), t = op(t);
    }
    function bf() {
      Ur = null, zi = null, rl = !1, Gs = !1;
    }
    function iC() {
      No !== null && (Z0(No), No = null);
    }
    function Ar() {
      return rl;
    }
    function Jy(e) {
      No === null ? No = [e] : No.push(e);
    }
    var gx = k.ReactCurrentBatchConfig, Sx = null;
    function Ex() {
      return gx.transition;
    }
    var al = {
      recordUnsafeLifecycleWarnings: function(e, t) {
      },
      flushPendingUnsafeLifecycleWarnings: function() {
      },
      recordLegacyContextWarning: function(e, t) {
      },
      flushLegacyContextWarning: function() {
      },
      discardPendingWarnings: function() {
      }
    };
    {
      var Cx = function(e) {
        for (var t = null, a = e; a !== null; )
          a.mode & Kt && (t = a), a = a.return;
        return t;
      }, Ks = function(e) {
        var t = [];
        return e.forEach(function(a) {
          t.push(a);
        }), t.sort().join(", ");
      }, dp = [], pp = [], vp = [], hp = [], mp = [], yp = [], qs = /* @__PURE__ */ new Set();
      al.recordUnsafeLifecycleWarnings = function(e, t) {
        qs.has(e.type) || (typeof t.componentWillMount == "function" && // Don't warn about react-lifecycles-compat polyfilled components.
        t.componentWillMount.__suppressDeprecationWarning !== !0 && dp.push(e), e.mode & Kt && typeof t.UNSAFE_componentWillMount == "function" && pp.push(e), typeof t.componentWillReceiveProps == "function" && t.componentWillReceiveProps.__suppressDeprecationWarning !== !0 && vp.push(e), e.mode & Kt && typeof t.UNSAFE_componentWillReceiveProps == "function" && hp.push(e), typeof t.componentWillUpdate == "function" && t.componentWillUpdate.__suppressDeprecationWarning !== !0 && mp.push(e), e.mode & Kt && typeof t.UNSAFE_componentWillUpdate == "function" && yp.push(e));
      }, al.flushPendingUnsafeLifecycleWarnings = function() {
        var e = /* @__PURE__ */ new Set();
        dp.length > 0 && (dp.forEach(function(w) {
          e.add(We(w) || "Component"), qs.add(w.type);
        }), dp = []);
        var t = /* @__PURE__ */ new Set();
        pp.length > 0 && (pp.forEach(function(w) {
          t.add(We(w) || "Component"), qs.add(w.type);
        }), pp = []);
        var a = /* @__PURE__ */ new Set();
        vp.length > 0 && (vp.forEach(function(w) {
          a.add(We(w) || "Component"), qs.add(w.type);
        }), vp = []);
        var i = /* @__PURE__ */ new Set();
        hp.length > 0 && (hp.forEach(function(w) {
          i.add(We(w) || "Component"), qs.add(w.type);
        }), hp = []);
        var u = /* @__PURE__ */ new Set();
        mp.length > 0 && (mp.forEach(function(w) {
          u.add(We(w) || "Component"), qs.add(w.type);
        }), mp = []);
        var s = /* @__PURE__ */ new Set();
        if (yp.length > 0 && (yp.forEach(function(w) {
          s.add(We(w) || "Component"), qs.add(w.type);
        }), yp = []), t.size > 0) {
          var f = Ks(t);
          S(`Using UNSAFE_componentWillMount in strict mode is not recommended and may indicate bugs in your code. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move code with side effects to componentDidMount, and set initial state in the constructor.

Please update the following components: %s`, f);
        }
        if (i.size > 0) {
          var p = Ks(i);
          S(`Using UNSAFE_componentWillReceiveProps in strict mode is not recommended and may indicate bugs in your code. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move data fetching code or side effects to componentDidUpdate.
* If you're updating state whenever props change, refactor your code to use memoization techniques or move it to static getDerivedStateFromProps. Learn more at: https://reactjs.org/link/derived-state

Please update the following components: %s`, p);
        }
        if (s.size > 0) {
          var v = Ks(s);
          S(`Using UNSAFE_componentWillUpdate in strict mode is not recommended and may indicate bugs in your code. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move data fetching code or side effects to componentDidUpdate.

Please update the following components: %s`, v);
        }
        if (e.size > 0) {
          var y = Ks(e);
          Ee(`componentWillMount has been renamed, and is not recommended for use. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move code with side effects to componentDidMount, and set initial state in the constructor.
* Rename componentWillMount to UNSAFE_componentWillMount to suppress this warning in non-strict mode. In React 18.x, only the UNSAFE_ name will work. To rename all deprecated lifecycles to their new names, you can run \`npx react-codemod rename-unsafe-lifecycles\` in your project source folder.

Please update the following components: %s`, y);
        }
        if (a.size > 0) {
          var g = Ks(a);
          Ee(`componentWillReceiveProps has been renamed, and is not recommended for use. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move data fetching code or side effects to componentDidUpdate.
* If you're updating state whenever props change, refactor your code to use memoization techniques or move it to static getDerivedStateFromProps. Learn more at: https://reactjs.org/link/derived-state
* Rename componentWillReceiveProps to UNSAFE_componentWillReceiveProps to suppress this warning in non-strict mode. In React 18.x, only the UNSAFE_ name will work. To rename all deprecated lifecycles to their new names, you can run \`npx react-codemod rename-unsafe-lifecycles\` in your project source folder.

Please update the following components: %s`, g);
        }
        if (u.size > 0) {
          var b = Ks(u);
          Ee(`componentWillUpdate has been renamed, and is not recommended for use. See https://reactjs.org/link/unsafe-component-lifecycles for details.

* Move data fetching code or side effects to componentDidUpdate.
* Rename componentWillUpdate to UNSAFE_componentWillUpdate to suppress this warning in non-strict mode. In React 18.x, only the UNSAFE_ name will work. To rename all deprecated lifecycles to their new names, you can run \`npx react-codemod rename-unsafe-lifecycles\` in your project source folder.

Please update the following components: %s`, b);
        }
      };
      var Bh = /* @__PURE__ */ new Map(), lC = /* @__PURE__ */ new Set();
      al.recordLegacyContextWarning = function(e, t) {
        var a = Cx(e);
        if (a === null) {
          S("Expected to find a StrictMode component in a strict mode tree. This error is likely caused by a bug in React. Please file an issue.");
          return;
        }
        if (!lC.has(e.type)) {
          var i = Bh.get(a);
          (e.type.contextTypes != null || e.type.childContextTypes != null || t !== null && typeof t.getChildContext == "function") && (i === void 0 && (i = [], Bh.set(a, i)), i.push(e));
        }
      }, al.flushLegacyContextWarning = function() {
        Bh.forEach(function(e, t) {
          if (e.length !== 0) {
            var a = e[0], i = /* @__PURE__ */ new Set();
            e.forEach(function(s) {
              i.add(We(s) || "Component"), lC.add(s.type);
            });
            var u = Ks(i);
            try {
              Qt(a), S(`Legacy context API has been detected within a strict-mode tree.

The old API will be supported in all 16.x releases, but applications using it should migrate to the new version.

Please update the following components: %s

Learn more about this warning here: https://reactjs.org/link/legacy-context`, u);
            } finally {
              cn();
            }
          }
        });
      }, al.discardPendingWarnings = function() {
        dp = [], pp = [], vp = [], hp = [], mp = [], yp = [], Bh = /* @__PURE__ */ new Map();
      };
    }
    var eg, tg, ng, rg, ag, uC = function(e, t) {
    };
    eg = !1, tg = !1, ng = {}, rg = {}, ag = {}, uC = function(e, t) {
      if (!(e === null || typeof e != "object") && !(!e._store || e._store.validated || e.key != null)) {
        if (typeof e._store != "object")
          throw new Error("React Component in warnForMissingKey should have a _store. This error is likely caused by a bug in React. Please file an issue.");
        e._store.validated = !0;
        var a = We(t) || "Component";
        rg[a] || (rg[a] = !0, S('Each child in a list should have a unique "key" prop. See https://reactjs.org/link/warning-keys for more information.'));
      }
    };
    function Rx(e) {
      return e.prototype && e.prototype.isReactComponent;
    }
    function gp(e, t, a) {
      var i = a.ref;
      if (i !== null && typeof i != "function" && typeof i != "object") {
        if ((e.mode & Kt || V) && // We warn in ReactElement.js if owner and self are equal for string refs
        // because these cannot be automatically converted to an arrow function
        // using a codemod. Therefore, we don't have to warn about string refs again.
        !(a._owner && a._self && a._owner.stateNode !== a._self) && // Will already throw with "Function components cannot have string refs"
        !(a._owner && a._owner.tag !== ce) && // Will already warn with "Function components cannot be given refs"
        !(typeof a.type == "function" && !Rx(a.type)) && // Will already throw with "Element ref was specified as a string (someStringRef) but no owner was set"
        a._owner) {
          var u = We(e) || "Component";
          ng[u] || (S('Component "%s" contains the string ref "%s". Support for string refs will be removed in a future major release. We recommend using useRef() or createRef() instead. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-string-ref', u, i), ng[u] = !0);
        }
        if (a._owner) {
          var s = a._owner, f;
          if (s) {
            var p = s;
            if (p.tag !== ce)
              throw new Error("Function components cannot have string refs. We recommend using useRef() instead. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-string-ref");
            f = p.stateNode;
          }
          if (!f)
            throw new Error("Missing owner for string ref " + i + ". This error is likely caused by a bug in React. Please file an issue.");
          var v = f;
          ci(i, "ref");
          var y = "" + i;
          if (t !== null && t.ref !== null && typeof t.ref == "function" && t.ref._stringRef === y)
            return t.ref;
          var g = function(b) {
            var w = v.refs;
            b === null ? delete w[y] : w[y] = b;
          };
          return g._stringRef = y, g;
        } else {
          if (typeof i != "string")
            throw new Error("Expected ref to be a function, a string, an object returned by React.createRef(), or null.");
          if (!a._owner)
            throw new Error("Element ref was specified as a string (" + i + `) but no owner was set. This could happen for one of the following reasons:
1. You may be adding a ref to a function component
2. You may be adding a ref to a component that was not created inside a component's render method
3. You have multiple copies of React loaded
See https://reactjs.org/link/refs-must-have-owner for more information.`);
        }
      }
      return i;
    }
    function Ih(e, t) {
      var a = Object.prototype.toString.call(t);
      throw new Error("Objects are not valid as a React child (found: " + (a === "[object Object]" ? "object with keys {" + Object.keys(t).join(", ") + "}" : a) + "). If you meant to render a collection of children, use an array instead.");
    }
    function Yh(e) {
      {
        var t = We(e) || "Component";
        if (ag[t])
          return;
        ag[t] = !0, S("Functions are not valid as a React child. This may happen if you return a Component instead of <Component /> from render. Or maybe you meant to call this function rather than return it.");
      }
    }
    function oC(e) {
      var t = e._payload, a = e._init;
      return a(t);
    }
    function sC(e) {
      function t(O, P) {
        if (e) {
          var L = O.deletions;
          L === null ? (O.deletions = [P], O.flags |= ka) : L.push(P);
        }
      }
      function a(O, P) {
        if (!e)
          return null;
        for (var L = P; L !== null; )
          t(O, L), L = L.sibling;
        return null;
      }
      function i(O, P) {
        for (var L = /* @__PURE__ */ new Map(), q = P; q !== null; )
          q.key !== null ? L.set(q.key, q) : L.set(q.index, q), q = q.sibling;
        return L;
      }
      function u(O, P) {
        var L = ic(O, P);
        return L.index = 0, L.sibling = null, L;
      }
      function s(O, P, L) {
        if (O.index = L, !e)
          return O.flags |= Ri, P;
        var q = O.alternate;
        if (q !== null) {
          var pe = q.index;
          return pe < P ? (O.flags |= mn, P) : pe;
        } else
          return O.flags |= mn, P;
      }
      function f(O) {
        return e && O.alternate === null && (O.flags |= mn), O;
      }
      function p(O, P, L, q) {
        if (P === null || P.tag !== Ve) {
          var pe = JS(L, O.mode, q);
          return pe.return = O, pe;
        } else {
          var oe = u(P, L);
          return oe.return = O, oe;
        }
      }
      function v(O, P, L, q) {
        var pe = L.type;
        if (pe === di)
          return g(O, P, L.props.children, q, L.key);
        if (P !== null && (P.elementType === pe || // Keep this check inline so it only runs on the false path:
        vR(P, L) || // Lazy types should reconcile their resolved type.
        // We need to do this after the Hot Reloading check above,
        // because hot reloading has different semantics than prod because
        // it doesn't resuspend. So we can't let the call below suspend.
        typeof pe == "object" && pe !== null && pe.$$typeof === Ge && oC(pe) === P.type)) {
          var oe = u(P, L.props);
          return oe.ref = gp(O, P, L), oe.return = O, oe._debugSource = L._source, oe._debugOwner = L._owner, oe;
        }
        var Ye = ZS(L, O.mode, q);
        return Ye.ref = gp(O, P, L), Ye.return = O, Ye;
      }
      function y(O, P, L, q) {
        if (P === null || P.tag !== Se || P.stateNode.containerInfo !== L.containerInfo || P.stateNode.implementation !== L.implementation) {
          var pe = eE(L, O.mode, q);
          return pe.return = O, pe;
        } else {
          var oe = u(P, L.children || []);
          return oe.return = O, oe;
        }
      }
      function g(O, P, L, q, pe) {
        if (P === null || P.tag !== at) {
          var oe = Yo(L, O.mode, q, pe);
          return oe.return = O, oe;
        } else {
          var Ye = u(P, L);
          return Ye.return = O, Ye;
        }
      }
      function b(O, P, L) {
        if (typeof P == "string" && P !== "" || typeof P == "number") {
          var q = JS("" + P, O.mode, L);
          return q.return = O, q;
        }
        if (typeof P == "object" && P !== null) {
          switch (P.$$typeof) {
            case _r: {
              var pe = ZS(P, O.mode, L);
              return pe.ref = gp(O, null, P), pe.return = O, pe;
            }
            case rr: {
              var oe = eE(P, O.mode, L);
              return oe.return = O, oe;
            }
            case Ge: {
              var Ye = P._payload, Xe = P._init;
              return b(O, Xe(Ye), L);
            }
          }
          if (st(P) || Je(P)) {
            var Xt = Yo(P, O.mode, L, null);
            return Xt.return = O, Xt;
          }
          Ih(O, P);
        }
        return typeof P == "function" && Yh(O), null;
      }
      function w(O, P, L, q) {
        var pe = P !== null ? P.key : null;
        if (typeof L == "string" && L !== "" || typeof L == "number")
          return pe !== null ? null : p(O, P, "" + L, q);
        if (typeof L == "object" && L !== null) {
          switch (L.$$typeof) {
            case _r:
              return L.key === pe ? v(O, P, L, q) : null;
            case rr:
              return L.key === pe ? y(O, P, L, q) : null;
            case Ge: {
              var oe = L._payload, Ye = L._init;
              return w(O, P, Ye(oe), q);
            }
          }
          if (st(L) || Je(L))
            return pe !== null ? null : g(O, P, L, q, null);
          Ih(O, L);
        }
        return typeof L == "function" && Yh(O), null;
      }
      function N(O, P, L, q, pe) {
        if (typeof q == "string" && q !== "" || typeof q == "number") {
          var oe = O.get(L) || null;
          return p(P, oe, "" + q, pe);
        }
        if (typeof q == "object" && q !== null) {
          switch (q.$$typeof) {
            case _r: {
              var Ye = O.get(q.key === null ? L : q.key) || null;
              return v(P, Ye, q, pe);
            }
            case rr: {
              var Xe = O.get(q.key === null ? L : q.key) || null;
              return y(P, Xe, q, pe);
            }
            case Ge:
              var Xt = q._payload, Ut = q._init;
              return N(O, P, L, Ut(Xt), pe);
          }
          if (st(q) || Je(q)) {
            var Gn = O.get(L) || null;
            return g(P, Gn, q, pe, null);
          }
          Ih(P, q);
        }
        return typeof q == "function" && Yh(P), null;
      }
      function A(O, P, L) {
        {
          if (typeof O != "object" || O === null)
            return P;
          switch (O.$$typeof) {
            case _r:
            case rr:
              uC(O, L);
              var q = O.key;
              if (typeof q != "string")
                break;
              if (P === null) {
                P = /* @__PURE__ */ new Set(), P.add(q);
                break;
              }
              if (!P.has(q)) {
                P.add(q);
                break;
              }
              S("Encountered two children with the same key, `%s`. Keys should be unique so that components maintain their identity across updates. Non-unique keys may cause children to be duplicated and/or omitted — the behavior is unsupported and could change in a future version.", q);
              break;
            case Ge:
              var pe = O._payload, oe = O._init;
              A(oe(pe), P, L);
              break;
          }
        }
        return P;
      }
      function H(O, P, L, q) {
        for (var pe = null, oe = 0; oe < L.length; oe++) {
          var Ye = L[oe];
          pe = A(Ye, pe, O);
        }
        for (var Xe = null, Xt = null, Ut = P, Gn = 0, At = 0, Pn = null; Ut !== null && At < L.length; At++) {
          Ut.index > At ? (Pn = Ut, Ut = null) : Pn = Ut.sibling;
          var la = w(O, Ut, L[At], q);
          if (la === null) {
            Ut === null && (Ut = Pn);
            break;
          }
          e && Ut && la.alternate === null && t(O, Ut), Gn = s(la, Gn, At), Xt === null ? Xe = la : Xt.sibling = la, Xt = la, Ut = Pn;
        }
        if (At === L.length) {
          if (a(O, Ut), Ar()) {
            var Ir = At;
            Qs(O, Ir);
          }
          return Xe;
        }
        if (Ut === null) {
          for (; At < L.length; At++) {
            var si = b(O, L[At], q);
            si !== null && (Gn = s(si, Gn, At), Xt === null ? Xe = si : Xt.sibling = si, Xt = si);
          }
          if (Ar()) {
            var Ca = At;
            Qs(O, Ca);
          }
          return Xe;
        }
        for (var Ra = i(O, Ut); At < L.length; At++) {
          var ua = N(Ra, O, At, L[At], q);
          ua !== null && (e && ua.alternate !== null && Ra.delete(ua.key === null ? At : ua.key), Gn = s(ua, Gn, At), Xt === null ? Xe = ua : Xt.sibling = ua, Xt = ua);
        }
        if (e && Ra.forEach(function($f) {
          return t(O, $f);
        }), Ar()) {
          var Qu = At;
          Qs(O, Qu);
        }
        return Xe;
      }
      function ue(O, P, L, q) {
        var pe = Je(L);
        if (typeof pe != "function")
          throw new Error("An object is not an iterable. This error is likely caused by a bug in React. Please file an issue.");
        {
          typeof Symbol == "function" && // $FlowFixMe Flow doesn't know about toStringTag
          L[Symbol.toStringTag] === "Generator" && (tg || S("Using Generators as children is unsupported and will likely yield unexpected results because enumerating a generator mutates it. You may convert it to an array with `Array.from()` or the `[...spread]` operator before rendering. Keep in mind you might need to polyfill these features for older browsers."), tg = !0), L.entries === pe && (eg || S("Using Maps as children is not supported. Use an array of keyed ReactElements instead."), eg = !0);
          var oe = pe.call(L);
          if (oe)
            for (var Ye = null, Xe = oe.next(); !Xe.done; Xe = oe.next()) {
              var Xt = Xe.value;
              Ye = A(Xt, Ye, O);
            }
        }
        var Ut = pe.call(L);
        if (Ut == null)
          throw new Error("An iterable object provided no iterator.");
        for (var Gn = null, At = null, Pn = P, la = 0, Ir = 0, si = null, Ca = Ut.next(); Pn !== null && !Ca.done; Ir++, Ca = Ut.next()) {
          Pn.index > Ir ? (si = Pn, Pn = null) : si = Pn.sibling;
          var Ra = w(O, Pn, Ca.value, q);
          if (Ra === null) {
            Pn === null && (Pn = si);
            break;
          }
          e && Pn && Ra.alternate === null && t(O, Pn), la = s(Ra, la, Ir), At === null ? Gn = Ra : At.sibling = Ra, At = Ra, Pn = si;
        }
        if (Ca.done) {
          if (a(O, Pn), Ar()) {
            var ua = Ir;
            Qs(O, ua);
          }
          return Gn;
        }
        if (Pn === null) {
          for (; !Ca.done; Ir++, Ca = Ut.next()) {
            var Qu = b(O, Ca.value, q);
            Qu !== null && (la = s(Qu, la, Ir), At === null ? Gn = Qu : At.sibling = Qu, At = Qu);
          }
          if (Ar()) {
            var $f = Ir;
            Qs(O, $f);
          }
          return Gn;
        }
        for (var qp = i(O, Pn); !Ca.done; Ir++, Ca = Ut.next()) {
          var Zl = N(qp, O, Ir, Ca.value, q);
          Zl !== null && (e && Zl.alternate !== null && qp.delete(Zl.key === null ? Ir : Zl.key), la = s(Zl, la, Ir), At === null ? Gn = Zl : At.sibling = Zl, At = Zl);
        }
        if (e && qp.forEach(function(G_) {
          return t(O, G_);
        }), Ar()) {
          var W_ = Ir;
          Qs(O, W_);
        }
        return Gn;
      }
      function ze(O, P, L, q) {
        if (P !== null && P.tag === Ve) {
          a(O, P.sibling);
          var pe = u(P, L);
          return pe.return = O, pe;
        }
        a(O, P);
        var oe = JS(L, O.mode, q);
        return oe.return = O, oe;
      }
      function be(O, P, L, q) {
        for (var pe = L.key, oe = P; oe !== null; ) {
          if (oe.key === pe) {
            var Ye = L.type;
            if (Ye === di) {
              if (oe.tag === at) {
                a(O, oe.sibling);
                var Xe = u(oe, L.props.children);
                return Xe.return = O, Xe._debugSource = L._source, Xe._debugOwner = L._owner, Xe;
              }
            } else if (oe.elementType === Ye || // Keep this check inline so it only runs on the false path:
            vR(oe, L) || // Lazy types should reconcile their resolved type.
            // We need to do this after the Hot Reloading check above,
            // because hot reloading has different semantics than prod because
            // it doesn't resuspend. So we can't let the call below suspend.
            typeof Ye == "object" && Ye !== null && Ye.$$typeof === Ge && oC(Ye) === oe.type) {
              a(O, oe.sibling);
              var Xt = u(oe, L.props);
              return Xt.ref = gp(O, oe, L), Xt.return = O, Xt._debugSource = L._source, Xt._debugOwner = L._owner, Xt;
            }
            a(O, oe);
            break;
          } else
            t(O, oe);
          oe = oe.sibling;
        }
        if (L.type === di) {
          var Ut = Yo(L.props.children, O.mode, q, L.key);
          return Ut.return = O, Ut;
        } else {
          var Gn = ZS(L, O.mode, q);
          return Gn.ref = gp(O, P, L), Gn.return = O, Gn;
        }
      }
      function wt(O, P, L, q) {
        for (var pe = L.key, oe = P; oe !== null; ) {
          if (oe.key === pe)
            if (oe.tag === Se && oe.stateNode.containerInfo === L.containerInfo && oe.stateNode.implementation === L.implementation) {
              a(O, oe.sibling);
              var Ye = u(oe, L.children || []);
              return Ye.return = O, Ye;
            } else {
              a(O, oe);
              break;
            }
          else
            t(O, oe);
          oe = oe.sibling;
        }
        var Xe = eE(L, O.mode, q);
        return Xe.return = O, Xe;
      }
      function yt(O, P, L, q) {
        var pe = typeof L == "object" && L !== null && L.type === di && L.key === null;
        if (pe && (L = L.props.children), typeof L == "object" && L !== null) {
          switch (L.$$typeof) {
            case _r:
              return f(be(O, P, L, q));
            case rr:
              return f(wt(O, P, L, q));
            case Ge:
              var oe = L._payload, Ye = L._init;
              return yt(O, P, Ye(oe), q);
          }
          if (st(L))
            return H(O, P, L, q);
          if (Je(L))
            return ue(O, P, L, q);
          Ih(O, L);
        }
        return typeof L == "string" && L !== "" || typeof L == "number" ? f(ze(O, P, "" + L, q)) : (typeof L == "function" && Yh(O), a(O, P));
      }
      return yt;
    }
    var _f = sC(!0), cC = sC(!1);
    function Tx(e, t) {
      if (e !== null && t.child !== e.child)
        throw new Error("Resuming work not yet implemented.");
      if (t.child !== null) {
        var a = t.child, i = ic(a, a.pendingProps);
        for (t.child = i, i.return = t; a.sibling !== null; )
          a = a.sibling, i = i.sibling = ic(a, a.pendingProps), i.return = t;
        i.sibling = null;
      }
    }
    function wx(e, t) {
      for (var a = e.child; a !== null; )
        f_(a, t), a = a.sibling;
    }
    var ig = Oo(null), lg;
    lg = {};
    var $h = null, kf = null, ug = null, Qh = !1;
    function Wh() {
      $h = null, kf = null, ug = null, Qh = !1;
    }
    function fC() {
      Qh = !0;
    }
    function dC() {
      Qh = !1;
    }
    function pC(e, t, a) {
      aa(ig, t._currentValue, e), t._currentValue = a, t._currentRenderer !== void 0 && t._currentRenderer !== null && t._currentRenderer !== lg && S("Detected multiple renderers concurrently rendering the same context provider. This is currently unsupported."), t._currentRenderer = lg;
    }
    function og(e, t) {
      var a = ig.current;
      ra(ig, t), e._currentValue = a;
    }
    function sg(e, t, a) {
      for (var i = e; i !== null; ) {
        var u = i.alternate;
        if (ku(i.childLanes, t) ? u !== null && !ku(u.childLanes, t) && (u.childLanes = et(u.childLanes, t)) : (i.childLanes = et(i.childLanes, t), u !== null && (u.childLanes = et(u.childLanes, t))), i === a)
          break;
        i = i.return;
      }
      i !== a && S("Expected to find the propagation root when scheduling context work. This error is likely caused by a bug in React. Please file an issue.");
    }
    function xx(e, t, a) {
      bx(e, t, a);
    }
    function bx(e, t, a) {
      var i = e.child;
      for (i !== null && (i.return = e); i !== null; ) {
        var u = void 0, s = i.dependencies;
        if (s !== null) {
          u = i.child;
          for (var f = s.firstContext; f !== null; ) {
            if (f.context === t) {
              if (i.tag === ce) {
                var p = Ts(a), v = Pu(Zt, p);
                v.tag = Kh;
                var y = i.updateQueue;
                if (y !== null) {
                  var g = y.shared, b = g.pending;
                  b === null ? v.next = v : (v.next = b.next, b.next = v), g.pending = v;
                }
              }
              i.lanes = et(i.lanes, a);
              var w = i.alternate;
              w !== null && (w.lanes = et(w.lanes, a)), sg(i.return, a, e), s.lanes = et(s.lanes, a);
              break;
            }
            f = f.next;
          }
        } else if (i.tag === qe)
          u = i.type === e.type ? null : i.child;
        else if (i.tag === Jt) {
          var N = i.return;
          if (N === null)
            throw new Error("We just came from a parent so we must have had a parent. This is a bug in React.");
          N.lanes = et(N.lanes, a);
          var A = N.alternate;
          A !== null && (A.lanes = et(A.lanes, a)), sg(N, a, e), u = i.sibling;
        } else
          u = i.child;
        if (u !== null)
          u.return = i;
        else
          for (u = i; u !== null; ) {
            if (u === e) {
              u = null;
              break;
            }
            var H = u.sibling;
            if (H !== null) {
              H.return = u.return, u = H;
              break;
            }
            u = u.return;
          }
        i = u;
      }
    }
    function Df(e, t) {
      $h = e, kf = null, ug = null;
      var a = e.dependencies;
      if (a !== null) {
        var i = a.firstContext;
        i !== null && (Jr(a.lanes, t) && Np(), a.firstContext = null);
      }
    }
    function tr(e) {
      Qh && S("Context can only be read while React is rendering. In classes, you can read it in the render method or getDerivedStateFromProps. In function components, you can read it directly in the function body, but not inside Hooks like useReducer() or useMemo().");
      var t = e._currentValue;
      if (ug !== e) {
        var a = {
          context: e,
          memoizedValue: t,
          next: null
        };
        if (kf === null) {
          if ($h === null)
            throw new Error("Context can only be read while React is rendering. In classes, you can read it in the render method or getDerivedStateFromProps. In function components, you can read it directly in the function body, but not inside Hooks like useReducer() or useMemo().");
          kf = a, $h.dependencies = {
            lanes: $,
            firstContext: a
          };
        } else
          kf = kf.next = a;
      }
      return t;
    }
    var Xs = null;
    function cg(e) {
      Xs === null ? Xs = [e] : Xs.push(e);
    }
    function _x() {
      if (Xs !== null) {
        for (var e = 0; e < Xs.length; e++) {
          var t = Xs[e], a = t.interleaved;
          if (a !== null) {
            t.interleaved = null;
            var i = a.next, u = t.pending;
            if (u !== null) {
              var s = u.next;
              u.next = i, a.next = s;
            }
            t.pending = a;
          }
        }
        Xs = null;
      }
    }
    function vC(e, t, a, i) {
      var u = t.interleaved;
      return u === null ? (a.next = a, cg(t)) : (a.next = u.next, u.next = a), t.interleaved = a, Gh(e, i);
    }
    function kx(e, t, a, i) {
      var u = t.interleaved;
      u === null ? (a.next = a, cg(t)) : (a.next = u.next, u.next = a), t.interleaved = a;
    }
    function Dx(e, t, a, i) {
      var u = t.interleaved;
      return u === null ? (a.next = a, cg(t)) : (a.next = u.next, u.next = a), t.interleaved = a, Gh(e, i);
    }
    function Fa(e, t) {
      return Gh(e, t);
    }
    var Ox = Gh;
    function Gh(e, t) {
      e.lanes = et(e.lanes, t);
      var a = e.alternate;
      a !== null && (a.lanes = et(a.lanes, t)), a === null && (e.flags & (mn | Gr)) !== De && cR(e);
      for (var i = e, u = e.return; u !== null; )
        u.childLanes = et(u.childLanes, t), a = u.alternate, a !== null ? a.childLanes = et(a.childLanes, t) : (u.flags & (mn | Gr)) !== De && cR(e), i = u, u = u.return;
      if (i.tag === J) {
        var s = i.stateNode;
        return s;
      } else
        return null;
    }
    var hC = 0, mC = 1, Kh = 2, fg = 3, qh = !1, dg, Xh;
    dg = !1, Xh = null;
    function pg(e) {
      var t = {
        baseState: e.memoizedState,
        firstBaseUpdate: null,
        lastBaseUpdate: null,
        shared: {
          pending: null,
          interleaved: null,
          lanes: $
        },
        effects: null
      };
      e.updateQueue = t;
    }
    function yC(e, t) {
      var a = t.updateQueue, i = e.updateQueue;
      if (a === i) {
        var u = {
          baseState: i.baseState,
          firstBaseUpdate: i.firstBaseUpdate,
          lastBaseUpdate: i.lastBaseUpdate,
          shared: i.shared,
          effects: i.effects
        };
        t.updateQueue = u;
      }
    }
    function Pu(e, t) {
      var a = {
        eventTime: e,
        lane: t,
        tag: hC,
        payload: null,
        callback: null,
        next: null
      };
      return a;
    }
    function zo(e, t, a) {
      var i = e.updateQueue;
      if (i === null)
        return null;
      var u = i.shared;
      if (Xh === u && !dg && (S("An update (setState, replaceState, or forceUpdate) was scheduled from inside an update function. Update functions should be pure, with zero side-effects. Consider using componentDidUpdate or a callback."), dg = !0), k1()) {
        var s = u.pending;
        return s === null ? t.next = t : (t.next = s.next, s.next = t), u.pending = t, Ox(e, a);
      } else
        return Dx(e, u, t, a);
    }
    function Zh(e, t, a) {
      var i = t.updateQueue;
      if (i !== null) {
        var u = i.shared;
        if (Ld(a)) {
          var s = u.lanes;
          s = Nd(s, e.pendingLanes);
          var f = et(s, a);
          u.lanes = f, ef(e, f);
        }
      }
    }
    function vg(e, t) {
      var a = e.updateQueue, i = e.alternate;
      if (i !== null) {
        var u = i.updateQueue;
        if (a === u) {
          var s = null, f = null, p = a.firstBaseUpdate;
          if (p !== null) {
            var v = p;
            do {
              var y = {
                eventTime: v.eventTime,
                lane: v.lane,
                tag: v.tag,
                payload: v.payload,
                callback: v.callback,
                next: null
              };
              f === null ? s = f = y : (f.next = y, f = y), v = v.next;
            } while (v !== null);
            f === null ? s = f = t : (f.next = t, f = t);
          } else
            s = f = t;
          a = {
            baseState: u.baseState,
            firstBaseUpdate: s,
            lastBaseUpdate: f,
            shared: u.shared,
            effects: u.effects
          }, e.updateQueue = a;
          return;
        }
      }
      var g = a.lastBaseUpdate;
      g === null ? a.firstBaseUpdate = t : g.next = t, a.lastBaseUpdate = t;
    }
    function Lx(e, t, a, i, u, s) {
      switch (a.tag) {
        case mC: {
          var f = a.payload;
          if (typeof f == "function") {
            fC();
            var p = f.call(s, i, u);
            {
              if (e.mode & Kt) {
                yn(!0);
                try {
                  f.call(s, i, u);
                } finally {
                  yn(!1);
                }
              }
              dC();
            }
            return p;
          }
          return f;
        }
        case fg:
          e.flags = e.flags & ~Xn | _e;
        case hC: {
          var v = a.payload, y;
          if (typeof v == "function") {
            fC(), y = v.call(s, i, u);
            {
              if (e.mode & Kt) {
                yn(!0);
                try {
                  v.call(s, i, u);
                } finally {
                  yn(!1);
                }
              }
              dC();
            }
          } else
            y = v;
          return y == null ? i : rt({}, i, y);
        }
        case Kh:
          return qh = !0, i;
      }
      return i;
    }
    function Jh(e, t, a, i) {
      var u = e.updateQueue;
      qh = !1, Xh = u.shared;
      var s = u.firstBaseUpdate, f = u.lastBaseUpdate, p = u.shared.pending;
      if (p !== null) {
        u.shared.pending = null;
        var v = p, y = v.next;
        v.next = null, f === null ? s = y : f.next = y, f = v;
        var g = e.alternate;
        if (g !== null) {
          var b = g.updateQueue, w = b.lastBaseUpdate;
          w !== f && (w === null ? b.firstBaseUpdate = y : w.next = y, b.lastBaseUpdate = v);
        }
      }
      if (s !== null) {
        var N = u.baseState, A = $, H = null, ue = null, ze = null, be = s;
        do {
          var wt = be.lane, yt = be.eventTime;
          if (ku(i, wt)) {
            if (ze !== null) {
              var P = {
                eventTime: yt,
                // This update is going to be committed so we never want uncommit
                // it. Using NoLane works because 0 is a subset of all bitmasks, so
                // this will never be skipped by the check above.
                lane: Dt,
                tag: be.tag,
                payload: be.payload,
                callback: be.callback,
                next: null
              };
              ze = ze.next = P;
            }
            N = Lx(e, u, be, N, t, a);
            var L = be.callback;
            if (L !== null && // If the update was already committed, we should not queue its
            // callback again.
            be.lane !== Dt) {
              e.flags |= an;
              var q = u.effects;
              q === null ? u.effects = [be] : q.push(be);
            }
          } else {
            var O = {
              eventTime: yt,
              lane: wt,
              tag: be.tag,
              payload: be.payload,
              callback: be.callback,
              next: null
            };
            ze === null ? (ue = ze = O, H = N) : ze = ze.next = O, A = et(A, wt);
          }
          if (be = be.next, be === null) {
            if (p = u.shared.pending, p === null)
              break;
            var pe = p, oe = pe.next;
            pe.next = null, be = oe, u.lastBaseUpdate = pe, u.shared.pending = null;
          }
        } while (!0);
        ze === null && (H = N), u.baseState = H, u.firstBaseUpdate = ue, u.lastBaseUpdate = ze;
        var Ye = u.shared.interleaved;
        if (Ye !== null) {
          var Xe = Ye;
          do
            A = et(A, Xe.lane), Xe = Xe.next;
          while (Xe !== Ye);
        } else s === null && (u.shared.lanes = $);
        $p(A), e.lanes = A, e.memoizedState = N;
      }
      Xh = null;
    }
    function Mx(e, t) {
      if (typeof e != "function")
        throw new Error("Invalid argument passed as callback. Expected a function. Instead " + ("received: " + e));
      e.call(t);
    }
    function gC() {
      qh = !1;
    }
    function em() {
      return qh;
    }
    function SC(e, t, a) {
      var i = t.effects;
      if (t.effects = null, i !== null)
        for (var u = 0; u < i.length; u++) {
          var s = i[u], f = s.callback;
          f !== null && (s.callback = null, Mx(f, a));
        }
    }
    var Sp = {}, Uo = Oo(Sp), Ep = Oo(Sp), tm = Oo(Sp);
    function nm(e) {
      if (e === Sp)
        throw new Error("Expected host context to exist. This error is likely caused by a bug in React. Please file an issue.");
      return e;
    }
    function EC() {
      var e = nm(tm.current);
      return e;
    }
    function hg(e, t) {
      aa(tm, t, e), aa(Ep, e, e), aa(Uo, Sp, e);
      var a = KT(t);
      ra(Uo, e), aa(Uo, a, e);
    }
    function Of(e) {
      ra(Uo, e), ra(Ep, e), ra(tm, e);
    }
    function mg() {
      var e = nm(Uo.current);
      return e;
    }
    function CC(e) {
      nm(tm.current);
      var t = nm(Uo.current), a = qT(t, e.type);
      t !== a && (aa(Ep, e, e), aa(Uo, a, e));
    }
    function yg(e) {
      Ep.current === e && (ra(Uo, e), ra(Ep, e));
    }
    var Nx = 0, RC = 1, TC = 1, Cp = 2, il = Oo(Nx);
    function gg(e, t) {
      return (e & t) !== 0;
    }
    function Lf(e) {
      return e & RC;
    }
    function Sg(e, t) {
      return e & RC | t;
    }
    function zx(e, t) {
      return e | t;
    }
    function Ao(e, t) {
      aa(il, t, e);
    }
    function Mf(e) {
      ra(il, e);
    }
    function Ux(e, t) {
      var a = e.memoizedState;
      return a !== null ? a.dehydrated !== null : (e.memoizedProps, !0);
    }
    function rm(e) {
      for (var t = e; t !== null; ) {
        if (t.tag === ke) {
          var a = t.memoizedState;
          if (a !== null) {
            var i = a.dehydrated;
            if (i === null || PE(i) || jy(i))
              return t;
          }
        } else if (t.tag === un && // revealOrder undefined can't be trusted because it don't
        // keep track of whether it suspended or not.
        t.memoizedProps.revealOrder !== void 0) {
          var u = (t.flags & _e) !== De;
          if (u)
            return t;
        } else if (t.child !== null) {
          t.child.return = t, t = t.child;
          continue;
        }
        if (t === e)
          return null;
        for (; t.sibling === null; ) {
          if (t.return === null || t.return === e)
            return null;
          t = t.return;
        }
        t.sibling.return = t.return, t = t.sibling;
      }
      return null;
    }
    var Ha = (
      /*   */
      0
    ), cr = (
      /* */
      1
    ), $l = (
      /*  */
      2
    ), fr = (
      /*    */
      4
    ), jr = (
      /*   */
      8
    ), Eg = [];
    function Cg() {
      for (var e = 0; e < Eg.length; e++) {
        var t = Eg[e];
        t._workInProgressVersionPrimary = null;
      }
      Eg.length = 0;
    }
    function Ax(e, t) {
      var a = t._getVersion, i = a(t._source);
      e.mutableSourceEagerHydrationData == null ? e.mutableSourceEagerHydrationData = [t, i] : e.mutableSourceEagerHydrationData.push(t, i);
    }
    var de = k.ReactCurrentDispatcher, Rp = k.ReactCurrentBatchConfig, Rg, Nf;
    Rg = /* @__PURE__ */ new Set();
    var Zs = $, qt = null, dr = null, pr = null, am = !1, Tp = !1, wp = 0, jx = 0, Fx = 25, B = null, Ui = null, jo = -1, Tg = !1;
    function Bt() {
      {
        var e = B;
        Ui === null ? Ui = [e] : Ui.push(e);
      }
    }
    function te() {
      {
        var e = B;
        Ui !== null && (jo++, Ui[jo] !== e && Hx(e));
      }
    }
    function zf(e) {
      e != null && !st(e) && S("%s received a final argument that is not an array (instead, received `%s`). When specified, the final argument must be an array.", B, typeof e);
    }
    function Hx(e) {
      {
        var t = We(qt);
        if (!Rg.has(t) && (Rg.add(t), Ui !== null)) {
          for (var a = "", i = 30, u = 0; u <= jo; u++) {
            for (var s = Ui[u], f = u === jo ? e : s, p = u + 1 + ". " + s; p.length < i; )
              p += " ";
            p += f + `
`, a += p;
          }
          S(`React has detected a change in the order of Hooks called by %s. This will lead to bugs and errors if not fixed. For more information, read the Rules of Hooks: https://reactjs.org/link/rules-of-hooks

   Previous render            Next render
   ------------------------------------------------------
%s   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`, t, a);
        }
      }
    }
    function ia() {
      throw new Error(`Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://reactjs.org/link/invalid-hook-call for tips about how to debug and fix this problem.`);
    }
    function wg(e, t) {
      if (Tg)
        return !1;
      if (t === null)
        return S("%s received a final argument during this render, but not during the previous render. Even though the final argument is optional, its type cannot change between renders.", B), !1;
      e.length !== t.length && S(`The final argument passed to %s changed size between renders. The order and size of this array must remain constant.

Previous: %s
Incoming: %s`, B, "[" + t.join(", ") + "]", "[" + e.join(", ") + "]");
      for (var a = 0; a < t.length && a < e.length; a++)
        if (!G(e[a], t[a]))
          return !1;
      return !0;
    }
    function Uf(e, t, a, i, u, s) {
      Zs = s, qt = t, Ui = e !== null ? e._debugHookTypes : null, jo = -1, Tg = e !== null && e.type !== t.type, t.memoizedState = null, t.updateQueue = null, t.lanes = $, e !== null && e.memoizedState !== null ? de.current = $C : Ui !== null ? de.current = YC : de.current = IC;
      var f = a(i, u);
      if (Tp) {
        var p = 0;
        do {
          if (Tp = !1, wp = 0, p >= Fx)
            throw new Error("Too many re-renders. React limits the number of renders to prevent an infinite loop.");
          p += 1, Tg = !1, dr = null, pr = null, t.updateQueue = null, jo = -1, de.current = QC, f = a(i, u);
        } while (Tp);
      }
      de.current = ym, t._debugHookTypes = Ui;
      var v = dr !== null && dr.next !== null;
      if (Zs = $, qt = null, dr = null, pr = null, B = null, Ui = null, jo = -1, e !== null && (e.flags & zn) !== (t.flags & zn) && // Disable this warning in legacy mode, because legacy Suspense is weird
      // and creates false positives. To make this work in legacy mode, we'd
      // need to mark fibers that commit in an incomplete state, somehow. For
      // now I'll disable the warning that most of the bugs that would trigger
      // it are either exclusive to concurrent mode or exist in both.
      (e.mode & vt) !== Oe && S("Internal React error: Expected static flag was missing. Please notify the React team."), am = !1, v)
        throw new Error("Rendered fewer hooks than expected. This may be caused by an accidental early return statement.");
      return f;
    }
    function Af() {
      var e = wp !== 0;
      return wp = 0, e;
    }
    function wC(e, t, a) {
      t.updateQueue = e.updateQueue, (t.mode & Nt) !== Oe ? t.flags &= -50333701 : t.flags &= -2053, e.lanes = ws(e.lanes, a);
    }
    function xC() {
      if (de.current = ym, am) {
        for (var e = qt.memoizedState; e !== null; ) {
          var t = e.queue;
          t !== null && (t.pending = null), e = e.next;
        }
        am = !1;
      }
      Zs = $, qt = null, dr = null, pr = null, Ui = null, jo = -1, B = null, FC = !1, Tp = !1, wp = 0;
    }
    function Ql() {
      var e = {
        memoizedState: null,
        baseState: null,
        baseQueue: null,
        queue: null,
        next: null
      };
      return pr === null ? qt.memoizedState = pr = e : pr = pr.next = e, pr;
    }
    function Ai() {
      var e;
      if (dr === null) {
        var t = qt.alternate;
        t !== null ? e = t.memoizedState : e = null;
      } else
        e = dr.next;
      var a;
      if (pr === null ? a = qt.memoizedState : a = pr.next, a !== null)
        pr = a, a = pr.next, dr = e;
      else {
        if (e === null)
          throw new Error("Rendered more hooks than during the previous render.");
        dr = e;
        var i = {
          memoizedState: dr.memoizedState,
          baseState: dr.baseState,
          baseQueue: dr.baseQueue,
          queue: dr.queue,
          next: null
        };
        pr === null ? qt.memoizedState = pr = i : pr = pr.next = i;
      }
      return pr;
    }
    function bC() {
      return {
        lastEffect: null,
        stores: null
      };
    }
    function xg(e, t) {
      return typeof t == "function" ? t(e) : t;
    }
    function bg(e, t, a) {
      var i = Ql(), u;
      a !== void 0 ? u = a(t) : u = t, i.memoizedState = i.baseState = u;
      var s = {
        pending: null,
        interleaved: null,
        lanes: $,
        dispatch: null,
        lastRenderedReducer: e,
        lastRenderedState: u
      };
      i.queue = s;
      var f = s.dispatch = Ix.bind(null, qt, s);
      return [i.memoizedState, f];
    }
    function _g(e, t, a) {
      var i = Ai(), u = i.queue;
      if (u === null)
        throw new Error("Should have a queue. This is likely a bug in React. Please file an issue.");
      u.lastRenderedReducer = e;
      var s = dr, f = s.baseQueue, p = u.pending;
      if (p !== null) {
        if (f !== null) {
          var v = f.next, y = p.next;
          f.next = y, p.next = v;
        }
        s.baseQueue !== f && S("Internal error: Expected work-in-progress queue to be a clone. This is a bug in React."), s.baseQueue = f = p, u.pending = null;
      }
      if (f !== null) {
        var g = f.next, b = s.baseState, w = null, N = null, A = null, H = g;
        do {
          var ue = H.lane;
          if (ku(Zs, ue)) {
            if (A !== null) {
              var be = {
                // This update is going to be committed so we never want uncommit
                // it. Using NoLane works because 0 is a subset of all bitmasks, so
                // this will never be skipped by the check above.
                lane: Dt,
                action: H.action,
                hasEagerState: H.hasEagerState,
                eagerState: H.eagerState,
                next: null
              };
              A = A.next = be;
            }
            if (H.hasEagerState)
              b = H.eagerState;
            else {
              var wt = H.action;
              b = e(b, wt);
            }
          } else {
            var ze = {
              lane: ue,
              action: H.action,
              hasEagerState: H.hasEagerState,
              eagerState: H.eagerState,
              next: null
            };
            A === null ? (N = A = ze, w = b) : A = A.next = ze, qt.lanes = et(qt.lanes, ue), $p(ue);
          }
          H = H.next;
        } while (H !== null && H !== g);
        A === null ? w = b : A.next = N, G(b, i.memoizedState) || Np(), i.memoizedState = b, i.baseState = w, i.baseQueue = A, u.lastRenderedState = b;
      }
      var yt = u.interleaved;
      if (yt !== null) {
        var O = yt;
        do {
          var P = O.lane;
          qt.lanes = et(qt.lanes, P), $p(P), O = O.next;
        } while (O !== yt);
      } else f === null && (u.lanes = $);
      var L = u.dispatch;
      return [i.memoizedState, L];
    }
    function kg(e, t, a) {
      var i = Ai(), u = i.queue;
      if (u === null)
        throw new Error("Should have a queue. This is likely a bug in React. Please file an issue.");
      u.lastRenderedReducer = e;
      var s = u.dispatch, f = u.pending, p = i.memoizedState;
      if (f !== null) {
        u.pending = null;
        var v = f.next, y = v;
        do {
          var g = y.action;
          p = e(p, g), y = y.next;
        } while (y !== v);
        G(p, i.memoizedState) || Np(), i.memoizedState = p, i.baseQueue === null && (i.baseState = p), u.lastRenderedState = p;
      }
      return [p, s];
    }
    function Ek(e, t, a) {
    }
    function Ck(e, t, a) {
    }
    function Dg(e, t, a) {
      var i = qt, u = Ql(), s, f = Ar();
      if (f) {
        if (a === void 0)
          throw new Error("Missing getServerSnapshot, which is required for server-rendered content. Will revert to client rendering.");
        s = a(), Nf || s !== a() && (S("The result of getServerSnapshot should be cached to avoid an infinite loop"), Nf = !0);
      } else {
        if (s = t(), !Nf) {
          var p = t();
          G(s, p) || (S("The result of getSnapshot should be cached to avoid an infinite loop"), Nf = !0);
        }
        var v = Am();
        if (v === null)
          throw new Error("Expected a work-in-progress root. This is a bug in React. Please file an issue.");
        Zc(v, Zs) || _C(i, t, s);
      }
      u.memoizedState = s;
      var y = {
        value: s,
        getSnapshot: t
      };
      return u.queue = y, sm(DC.bind(null, i, y, e), [e]), i.flags |= Wr, xp(cr | jr, kC.bind(null, i, y, s, t), void 0, null), s;
    }
    function im(e, t, a) {
      var i = qt, u = Ai(), s = t();
      if (!Nf) {
        var f = t();
        G(s, f) || (S("The result of getSnapshot should be cached to avoid an infinite loop"), Nf = !0);
      }
      var p = u.memoizedState, v = !G(p, s);
      v && (u.memoizedState = s, Np());
      var y = u.queue;
      if (_p(DC.bind(null, i, y, e), [e]), y.getSnapshot !== t || v || // Check if the susbcribe function changed. We can save some memory by
      // checking whether we scheduled a subscription effect above.
      pr !== null && pr.memoizedState.tag & cr) {
        i.flags |= Wr, xp(cr | jr, kC.bind(null, i, y, s, t), void 0, null);
        var g = Am();
        if (g === null)
          throw new Error("Expected a work-in-progress root. This is a bug in React. Please file an issue.");
        Zc(g, Zs) || _C(i, t, s);
      }
      return s;
    }
    function _C(e, t, a) {
      e.flags |= vo;
      var i = {
        getSnapshot: t,
        value: a
      }, u = qt.updateQueue;
      if (u === null)
        u = bC(), qt.updateQueue = u, u.stores = [i];
      else {
        var s = u.stores;
        s === null ? u.stores = [i] : s.push(i);
      }
    }
    function kC(e, t, a, i) {
      t.value = a, t.getSnapshot = i, OC(t) && LC(e);
    }
    function DC(e, t, a) {
      var i = function() {
        OC(t) && LC(e);
      };
      return a(i);
    }
    function OC(e) {
      var t = e.getSnapshot, a = e.value;
      try {
        var i = t();
        return !G(a, i);
      } catch {
        return !0;
      }
    }
    function LC(e) {
      var t = Fa(e, Be);
      t !== null && yr(t, e, Be, Zt);
    }
    function lm(e) {
      var t = Ql();
      typeof e == "function" && (e = e()), t.memoizedState = t.baseState = e;
      var a = {
        pending: null,
        interleaved: null,
        lanes: $,
        dispatch: null,
        lastRenderedReducer: xg,
        lastRenderedState: e
      };
      t.queue = a;
      var i = a.dispatch = Yx.bind(null, qt, a);
      return [t.memoizedState, i];
    }
    function Og(e) {
      return _g(xg);
    }
    function Lg(e) {
      return kg(xg);
    }
    function xp(e, t, a, i) {
      var u = {
        tag: e,
        create: t,
        destroy: a,
        deps: i,
        // Circular
        next: null
      }, s = qt.updateQueue;
      if (s === null)
        s = bC(), qt.updateQueue = s, s.lastEffect = u.next = u;
      else {
        var f = s.lastEffect;
        if (f === null)
          s.lastEffect = u.next = u;
        else {
          var p = f.next;
          f.next = u, u.next = p, s.lastEffect = u;
        }
      }
      return u;
    }
    function Mg(e) {
      var t = Ql();
      {
        var a = {
          current: e
        };
        return t.memoizedState = a, a;
      }
    }
    function um(e) {
      var t = Ai();
      return t.memoizedState;
    }
    function bp(e, t, a, i) {
      var u = Ql(), s = i === void 0 ? null : i;
      qt.flags |= e, u.memoizedState = xp(cr | t, a, void 0, s);
    }
    function om(e, t, a, i) {
      var u = Ai(), s = i === void 0 ? null : i, f = void 0;
      if (dr !== null) {
        var p = dr.memoizedState;
        if (f = p.destroy, s !== null) {
          var v = p.deps;
          if (wg(s, v)) {
            u.memoizedState = xp(t, a, f, s);
            return;
          }
        }
      }
      qt.flags |= e, u.memoizedState = xp(cr | t, a, f, s);
    }
    function sm(e, t) {
      return (qt.mode & Nt) !== Oe ? bp(Ti | Wr | xc, jr, e, t) : bp(Wr | xc, jr, e, t);
    }
    function _p(e, t) {
      return om(Wr, jr, e, t);
    }
    function Ng(e, t) {
      return bp(Ct, $l, e, t);
    }
    function cm(e, t) {
      return om(Ct, $l, e, t);
    }
    function zg(e, t) {
      var a = Ct;
      return a |= Wi, (qt.mode & Nt) !== Oe && (a |= _l), bp(a, fr, e, t);
    }
    function fm(e, t) {
      return om(Ct, fr, e, t);
    }
    function MC(e, t) {
      if (typeof t == "function") {
        var a = t, i = e();
        return a(i), function() {
          a(null);
        };
      } else if (t != null) {
        var u = t;
        u.hasOwnProperty("current") || S("Expected useImperativeHandle() first argument to either be a ref callback or React.createRef() object. Instead received: %s.", "an object with keys {" + Object.keys(u).join(", ") + "}");
        var s = e();
        return u.current = s, function() {
          u.current = null;
        };
      }
    }
    function Ug(e, t, a) {
      typeof t != "function" && S("Expected useImperativeHandle() second argument to be a function that creates a handle. Instead received: %s.", t !== null ? typeof t : "null");
      var i = a != null ? a.concat([e]) : null, u = Ct;
      return u |= Wi, (qt.mode & Nt) !== Oe && (u |= _l), bp(u, fr, MC.bind(null, t, e), i);
    }
    function dm(e, t, a) {
      typeof t != "function" && S("Expected useImperativeHandle() second argument to be a function that creates a handle. Instead received: %s.", t !== null ? typeof t : "null");
      var i = a != null ? a.concat([e]) : null;
      return om(Ct, fr, MC.bind(null, t, e), i);
    }
    function Px(e, t) {
    }
    var pm = Px;
    function Ag(e, t) {
      var a = Ql(), i = t === void 0 ? null : t;
      return a.memoizedState = [e, i], e;
    }
    function vm(e, t) {
      var a = Ai(), i = t === void 0 ? null : t, u = a.memoizedState;
      if (u !== null && i !== null) {
        var s = u[1];
        if (wg(i, s))
          return u[0];
      }
      return a.memoizedState = [e, i], e;
    }
    function jg(e, t) {
      var a = Ql(), i = t === void 0 ? null : t, u = e();
      return a.memoizedState = [u, i], u;
    }
    function hm(e, t) {
      var a = Ai(), i = t === void 0 ? null : t, u = a.memoizedState;
      if (u !== null && i !== null) {
        var s = u[1];
        if (wg(i, s))
          return u[0];
      }
      var f = e();
      return a.memoizedState = [f, i], f;
    }
    function Fg(e) {
      var t = Ql();
      return t.memoizedState = e, e;
    }
    function NC(e) {
      var t = Ai(), a = dr, i = a.memoizedState;
      return UC(t, i, e);
    }
    function zC(e) {
      var t = Ai();
      if (dr === null)
        return t.memoizedState = e, e;
      var a = dr.memoizedState;
      return UC(t, a, e);
    }
    function UC(e, t, a) {
      var i = !Dd(Zs);
      if (i) {
        if (!G(a, t)) {
          var u = Md();
          qt.lanes = et(qt.lanes, u), $p(u), e.baseState = !0;
        }
        return t;
      } else
        return e.baseState && (e.baseState = !1, Np()), e.memoizedState = a, a;
    }
    function Vx(e, t, a) {
      var i = Ua();
      jn(Qv(i, _i)), e(!0);
      var u = Rp.transition;
      Rp.transition = {};
      var s = Rp.transition;
      Rp.transition._updatedFibers = /* @__PURE__ */ new Set();
      try {
        e(!1), t();
      } finally {
        if (jn(i), Rp.transition = u, u === null && s._updatedFibers) {
          var f = s._updatedFibers.size;
          f > 10 && Ee("Detected a large number of updates inside startTransition. If this is due to a subscription please re-write it to use React provided hooks. Otherwise concurrent mode guarantees are off the table."), s._updatedFibers.clear();
        }
      }
    }
    function Hg() {
      var e = lm(!1), t = e[0], a = e[1], i = Vx.bind(null, a), u = Ql();
      return u.memoizedState = i, [t, i];
    }
    function AC() {
      var e = Og(), t = e[0], a = Ai(), i = a.memoizedState;
      return [t, i];
    }
    function jC() {
      var e = Lg(), t = e[0], a = Ai(), i = a.memoizedState;
      return [t, i];
    }
    var FC = !1;
    function Bx() {
      return FC;
    }
    function Pg() {
      var e = Ql(), t = Am(), a = t.identifierPrefix, i;
      if (Ar()) {
        var u = ix();
        i = ":" + a + "R" + u;
        var s = wp++;
        s > 0 && (i += "H" + s.toString(32)), i += ":";
      } else {
        var f = jx++;
        i = ":" + a + "r" + f.toString(32) + ":";
      }
      return e.memoizedState = i, i;
    }
    function mm() {
      var e = Ai(), t = e.memoizedState;
      return t;
    }
    function Ix(e, t, a) {
      typeof arguments[3] == "function" && S("State updates from the useState() and useReducer() Hooks don't support the second callback argument. To execute a side effect after rendering, declare it in the component body with useEffect().");
      var i = Bo(e), u = {
        lane: i,
        action: a,
        hasEagerState: !1,
        eagerState: null,
        next: null
      };
      if (HC(e))
        PC(t, u);
      else {
        var s = vC(e, t, u, i);
        if (s !== null) {
          var f = Ea();
          yr(s, e, i, f), VC(s, t, i);
        }
      }
      BC(e, i);
    }
    function Yx(e, t, a) {
      typeof arguments[3] == "function" && S("State updates from the useState() and useReducer() Hooks don't support the second callback argument. To execute a side effect after rendering, declare it in the component body with useEffect().");
      var i = Bo(e), u = {
        lane: i,
        action: a,
        hasEagerState: !1,
        eagerState: null,
        next: null
      };
      if (HC(e))
        PC(t, u);
      else {
        var s = e.alternate;
        if (e.lanes === $ && (s === null || s.lanes === $)) {
          var f = t.lastRenderedReducer;
          if (f !== null) {
            var p;
            p = de.current, de.current = ll;
            try {
              var v = t.lastRenderedState, y = f(v, a);
              if (u.hasEagerState = !0, u.eagerState = y, G(y, v)) {
                kx(e, t, u, i);
                return;
              }
            } catch {
            } finally {
              de.current = p;
            }
          }
        }
        var g = vC(e, t, u, i);
        if (g !== null) {
          var b = Ea();
          yr(g, e, i, b), VC(g, t, i);
        }
      }
      BC(e, i);
    }
    function HC(e) {
      var t = e.alternate;
      return e === qt || t !== null && t === qt;
    }
    function PC(e, t) {
      Tp = am = !0;
      var a = e.pending;
      a === null ? t.next = t : (t.next = a.next, a.next = t), e.pending = t;
    }
    function VC(e, t, a) {
      if (Ld(a)) {
        var i = t.lanes;
        i = Nd(i, e.pendingLanes);
        var u = et(i, a);
        t.lanes = u, ef(e, u);
      }
    }
    function BC(e, t, a) {
      vs(e, t);
    }
    var ym = {
      readContext: tr,
      useCallback: ia,
      useContext: ia,
      useEffect: ia,
      useImperativeHandle: ia,
      useInsertionEffect: ia,
      useLayoutEffect: ia,
      useMemo: ia,
      useReducer: ia,
      useRef: ia,
      useState: ia,
      useDebugValue: ia,
      useDeferredValue: ia,
      useTransition: ia,
      useMutableSource: ia,
      useSyncExternalStore: ia,
      useId: ia,
      unstable_isNewReconciler: Z
    }, IC = null, YC = null, $C = null, QC = null, Wl = null, ll = null, gm = null;
    {
      var Vg = function() {
        S("Context can only be read while React is rendering. In classes, you can read it in the render method or getDerivedStateFromProps. In function components, you can read it directly in the function body, but not inside Hooks like useReducer() or useMemo().");
      }, Ke = function() {
        S("Do not call Hooks inside useEffect(...), useMemo(...), or other built-in Hooks. You can only call Hooks at the top level of your React function. For more information, see https://reactjs.org/link/rules-of-hooks");
      };
      IC = {
        readContext: function(e) {
          return tr(e);
        },
        useCallback: function(e, t) {
          return B = "useCallback", Bt(), zf(t), Ag(e, t);
        },
        useContext: function(e) {
          return B = "useContext", Bt(), tr(e);
        },
        useEffect: function(e, t) {
          return B = "useEffect", Bt(), zf(t), sm(e, t);
        },
        useImperativeHandle: function(e, t, a) {
          return B = "useImperativeHandle", Bt(), zf(a), Ug(e, t, a);
        },
        useInsertionEffect: function(e, t) {
          return B = "useInsertionEffect", Bt(), zf(t), Ng(e, t);
        },
        useLayoutEffect: function(e, t) {
          return B = "useLayoutEffect", Bt(), zf(t), zg(e, t);
        },
        useMemo: function(e, t) {
          B = "useMemo", Bt(), zf(t);
          var a = de.current;
          de.current = Wl;
          try {
            return jg(e, t);
          } finally {
            de.current = a;
          }
        },
        useReducer: function(e, t, a) {
          B = "useReducer", Bt();
          var i = de.current;
          de.current = Wl;
          try {
            return bg(e, t, a);
          } finally {
            de.current = i;
          }
        },
        useRef: function(e) {
          return B = "useRef", Bt(), Mg(e);
        },
        useState: function(e) {
          B = "useState", Bt();
          var t = de.current;
          de.current = Wl;
          try {
            return lm(e);
          } finally {
            de.current = t;
          }
        },
        useDebugValue: function(e, t) {
          return B = "useDebugValue", Bt(), void 0;
        },
        useDeferredValue: function(e) {
          return B = "useDeferredValue", Bt(), Fg(e);
        },
        useTransition: function() {
          return B = "useTransition", Bt(), Hg();
        },
        useMutableSource: function(e, t, a) {
          return B = "useMutableSource", Bt(), void 0;
        },
        useSyncExternalStore: function(e, t, a) {
          return B = "useSyncExternalStore", Bt(), Dg(e, t, a);
        },
        useId: function() {
          return B = "useId", Bt(), Pg();
        },
        unstable_isNewReconciler: Z
      }, YC = {
        readContext: function(e) {
          return tr(e);
        },
        useCallback: function(e, t) {
          return B = "useCallback", te(), Ag(e, t);
        },
        useContext: function(e) {
          return B = "useContext", te(), tr(e);
        },
        useEffect: function(e, t) {
          return B = "useEffect", te(), sm(e, t);
        },
        useImperativeHandle: function(e, t, a) {
          return B = "useImperativeHandle", te(), Ug(e, t, a);
        },
        useInsertionEffect: function(e, t) {
          return B = "useInsertionEffect", te(), Ng(e, t);
        },
        useLayoutEffect: function(e, t) {
          return B = "useLayoutEffect", te(), zg(e, t);
        },
        useMemo: function(e, t) {
          B = "useMemo", te();
          var a = de.current;
          de.current = Wl;
          try {
            return jg(e, t);
          } finally {
            de.current = a;
          }
        },
        useReducer: function(e, t, a) {
          B = "useReducer", te();
          var i = de.current;
          de.current = Wl;
          try {
            return bg(e, t, a);
          } finally {
            de.current = i;
          }
        },
        useRef: function(e) {
          return B = "useRef", te(), Mg(e);
        },
        useState: function(e) {
          B = "useState", te();
          var t = de.current;
          de.current = Wl;
          try {
            return lm(e);
          } finally {
            de.current = t;
          }
        },
        useDebugValue: function(e, t) {
          return B = "useDebugValue", te(), void 0;
        },
        useDeferredValue: function(e) {
          return B = "useDeferredValue", te(), Fg(e);
        },
        useTransition: function() {
          return B = "useTransition", te(), Hg();
        },
        useMutableSource: function(e, t, a) {
          return B = "useMutableSource", te(), void 0;
        },
        useSyncExternalStore: function(e, t, a) {
          return B = "useSyncExternalStore", te(), Dg(e, t, a);
        },
        useId: function() {
          return B = "useId", te(), Pg();
        },
        unstable_isNewReconciler: Z
      }, $C = {
        readContext: function(e) {
          return tr(e);
        },
        useCallback: function(e, t) {
          return B = "useCallback", te(), vm(e, t);
        },
        useContext: function(e) {
          return B = "useContext", te(), tr(e);
        },
        useEffect: function(e, t) {
          return B = "useEffect", te(), _p(e, t);
        },
        useImperativeHandle: function(e, t, a) {
          return B = "useImperativeHandle", te(), dm(e, t, a);
        },
        useInsertionEffect: function(e, t) {
          return B = "useInsertionEffect", te(), cm(e, t);
        },
        useLayoutEffect: function(e, t) {
          return B = "useLayoutEffect", te(), fm(e, t);
        },
        useMemo: function(e, t) {
          B = "useMemo", te();
          var a = de.current;
          de.current = ll;
          try {
            return hm(e, t);
          } finally {
            de.current = a;
          }
        },
        useReducer: function(e, t, a) {
          B = "useReducer", te();
          var i = de.current;
          de.current = ll;
          try {
            return _g(e, t, a);
          } finally {
            de.current = i;
          }
        },
        useRef: function(e) {
          return B = "useRef", te(), um();
        },
        useState: function(e) {
          B = "useState", te();
          var t = de.current;
          de.current = ll;
          try {
            return Og(e);
          } finally {
            de.current = t;
          }
        },
        useDebugValue: function(e, t) {
          return B = "useDebugValue", te(), pm();
        },
        useDeferredValue: function(e) {
          return B = "useDeferredValue", te(), NC(e);
        },
        useTransition: function() {
          return B = "useTransition", te(), AC();
        },
        useMutableSource: function(e, t, a) {
          return B = "useMutableSource", te(), void 0;
        },
        useSyncExternalStore: function(e, t, a) {
          return B = "useSyncExternalStore", te(), im(e, t);
        },
        useId: function() {
          return B = "useId", te(), mm();
        },
        unstable_isNewReconciler: Z
      }, QC = {
        readContext: function(e) {
          return tr(e);
        },
        useCallback: function(e, t) {
          return B = "useCallback", te(), vm(e, t);
        },
        useContext: function(e) {
          return B = "useContext", te(), tr(e);
        },
        useEffect: function(e, t) {
          return B = "useEffect", te(), _p(e, t);
        },
        useImperativeHandle: function(e, t, a) {
          return B = "useImperativeHandle", te(), dm(e, t, a);
        },
        useInsertionEffect: function(e, t) {
          return B = "useInsertionEffect", te(), cm(e, t);
        },
        useLayoutEffect: function(e, t) {
          return B = "useLayoutEffect", te(), fm(e, t);
        },
        useMemo: function(e, t) {
          B = "useMemo", te();
          var a = de.current;
          de.current = gm;
          try {
            return hm(e, t);
          } finally {
            de.current = a;
          }
        },
        useReducer: function(e, t, a) {
          B = "useReducer", te();
          var i = de.current;
          de.current = gm;
          try {
            return kg(e, t, a);
          } finally {
            de.current = i;
          }
        },
        useRef: function(e) {
          return B = "useRef", te(), um();
        },
        useState: function(e) {
          B = "useState", te();
          var t = de.current;
          de.current = gm;
          try {
            return Lg(e);
          } finally {
            de.current = t;
          }
        },
        useDebugValue: function(e, t) {
          return B = "useDebugValue", te(), pm();
        },
        useDeferredValue: function(e) {
          return B = "useDeferredValue", te(), zC(e);
        },
        useTransition: function() {
          return B = "useTransition", te(), jC();
        },
        useMutableSource: function(e, t, a) {
          return B = "useMutableSource", te(), void 0;
        },
        useSyncExternalStore: function(e, t, a) {
          return B = "useSyncExternalStore", te(), im(e, t);
        },
        useId: function() {
          return B = "useId", te(), mm();
        },
        unstable_isNewReconciler: Z
      }, Wl = {
        readContext: function(e) {
          return Vg(), tr(e);
        },
        useCallback: function(e, t) {
          return B = "useCallback", Ke(), Bt(), Ag(e, t);
        },
        useContext: function(e) {
          return B = "useContext", Ke(), Bt(), tr(e);
        },
        useEffect: function(e, t) {
          return B = "useEffect", Ke(), Bt(), sm(e, t);
        },
        useImperativeHandle: function(e, t, a) {
          return B = "useImperativeHandle", Ke(), Bt(), Ug(e, t, a);
        },
        useInsertionEffect: function(e, t) {
          return B = "useInsertionEffect", Ke(), Bt(), Ng(e, t);
        },
        useLayoutEffect: function(e, t) {
          return B = "useLayoutEffect", Ke(), Bt(), zg(e, t);
        },
        useMemo: function(e, t) {
          B = "useMemo", Ke(), Bt();
          var a = de.current;
          de.current = Wl;
          try {
            return jg(e, t);
          } finally {
            de.current = a;
          }
        },
        useReducer: function(e, t, a) {
          B = "useReducer", Ke(), Bt();
          var i = de.current;
          de.current = Wl;
          try {
            return bg(e, t, a);
          } finally {
            de.current = i;
          }
        },
        useRef: function(e) {
          return B = "useRef", Ke(), Bt(), Mg(e);
        },
        useState: function(e) {
          B = "useState", Ke(), Bt();
          var t = de.current;
          de.current = Wl;
          try {
            return lm(e);
          } finally {
            de.current = t;
          }
        },
        useDebugValue: function(e, t) {
          return B = "useDebugValue", Ke(), Bt(), void 0;
        },
        useDeferredValue: function(e) {
          return B = "useDeferredValue", Ke(), Bt(), Fg(e);
        },
        useTransition: function() {
          return B = "useTransition", Ke(), Bt(), Hg();
        },
        useMutableSource: function(e, t, a) {
          return B = "useMutableSource", Ke(), Bt(), void 0;
        },
        useSyncExternalStore: function(e, t, a) {
          return B = "useSyncExternalStore", Ke(), Bt(), Dg(e, t, a);
        },
        useId: function() {
          return B = "useId", Ke(), Bt(), Pg();
        },
        unstable_isNewReconciler: Z
      }, ll = {
        readContext: function(e) {
          return Vg(), tr(e);
        },
        useCallback: function(e, t) {
          return B = "useCallback", Ke(), te(), vm(e, t);
        },
        useContext: function(e) {
          return B = "useContext", Ke(), te(), tr(e);
        },
        useEffect: function(e, t) {
          return B = "useEffect", Ke(), te(), _p(e, t);
        },
        useImperativeHandle: function(e, t, a) {
          return B = "useImperativeHandle", Ke(), te(), dm(e, t, a);
        },
        useInsertionEffect: function(e, t) {
          return B = "useInsertionEffect", Ke(), te(), cm(e, t);
        },
        useLayoutEffect: function(e, t) {
          return B = "useLayoutEffect", Ke(), te(), fm(e, t);
        },
        useMemo: function(e, t) {
          B = "useMemo", Ke(), te();
          var a = de.current;
          de.current = ll;
          try {
            return hm(e, t);
          } finally {
            de.current = a;
          }
        },
        useReducer: function(e, t, a) {
          B = "useReducer", Ke(), te();
          var i = de.current;
          de.current = ll;
          try {
            return _g(e, t, a);
          } finally {
            de.current = i;
          }
        },
        useRef: function(e) {
          return B = "useRef", Ke(), te(), um();
        },
        useState: function(e) {
          B = "useState", Ke(), te();
          var t = de.current;
          de.current = ll;
          try {
            return Og(e);
          } finally {
            de.current = t;
          }
        },
        useDebugValue: function(e, t) {
          return B = "useDebugValue", Ke(), te(), pm();
        },
        useDeferredValue: function(e) {
          return B = "useDeferredValue", Ke(), te(), NC(e);
        },
        useTransition: function() {
          return B = "useTransition", Ke(), te(), AC();
        },
        useMutableSource: function(e, t, a) {
          return B = "useMutableSource", Ke(), te(), void 0;
        },
        useSyncExternalStore: function(e, t, a) {
          return B = "useSyncExternalStore", Ke(), te(), im(e, t);
        },
        useId: function() {
          return B = "useId", Ke(), te(), mm();
        },
        unstable_isNewReconciler: Z
      }, gm = {
        readContext: function(e) {
          return Vg(), tr(e);
        },
        useCallback: function(e, t) {
          return B = "useCallback", Ke(), te(), vm(e, t);
        },
        useContext: function(e) {
          return B = "useContext", Ke(), te(), tr(e);
        },
        useEffect: function(e, t) {
          return B = "useEffect", Ke(), te(), _p(e, t);
        },
        useImperativeHandle: function(e, t, a) {
          return B = "useImperativeHandle", Ke(), te(), dm(e, t, a);
        },
        useInsertionEffect: function(e, t) {
          return B = "useInsertionEffect", Ke(), te(), cm(e, t);
        },
        useLayoutEffect: function(e, t) {
          return B = "useLayoutEffect", Ke(), te(), fm(e, t);
        },
        useMemo: function(e, t) {
          B = "useMemo", Ke(), te();
          var a = de.current;
          de.current = ll;
          try {
            return hm(e, t);
          } finally {
            de.current = a;
          }
        },
        useReducer: function(e, t, a) {
          B = "useReducer", Ke(), te();
          var i = de.current;
          de.current = ll;
          try {
            return kg(e, t, a);
          } finally {
            de.current = i;
          }
        },
        useRef: function(e) {
          return B = "useRef", Ke(), te(), um();
        },
        useState: function(e) {
          B = "useState", Ke(), te();
          var t = de.current;
          de.current = ll;
          try {
            return Lg(e);
          } finally {
            de.current = t;
          }
        },
        useDebugValue: function(e, t) {
          return B = "useDebugValue", Ke(), te(), pm();
        },
        useDeferredValue: function(e) {
          return B = "useDeferredValue", Ke(), te(), zC(e);
        },
        useTransition: function() {
          return B = "useTransition", Ke(), te(), jC();
        },
        useMutableSource: function(e, t, a) {
          return B = "useMutableSource", Ke(), te(), void 0;
        },
        useSyncExternalStore: function(e, t, a) {
          return B = "useSyncExternalStore", Ke(), te(), im(e, t);
        },
        useId: function() {
          return B = "useId", Ke(), te(), mm();
        },
        unstable_isNewReconciler: Z
      };
    }
    var Fo = j.unstable_now, WC = 0, Sm = -1, kp = -1, Em = -1, Bg = !1, Cm = !1;
    function GC() {
      return Bg;
    }
    function $x() {
      Cm = !0;
    }
    function Qx() {
      Bg = !1, Cm = !1;
    }
    function Wx() {
      Bg = Cm, Cm = !1;
    }
    function KC() {
      return WC;
    }
    function qC() {
      WC = Fo();
    }
    function Ig(e) {
      kp = Fo(), e.actualStartTime < 0 && (e.actualStartTime = Fo());
    }
    function XC(e) {
      kp = -1;
    }
    function Rm(e, t) {
      if (kp >= 0) {
        var a = Fo() - kp;
        e.actualDuration += a, t && (e.selfBaseDuration = a), kp = -1;
      }
    }
    function Gl(e) {
      if (Sm >= 0) {
        var t = Fo() - Sm;
        Sm = -1;
        for (var a = e.return; a !== null; ) {
          switch (a.tag) {
            case J:
              var i = a.stateNode;
              i.effectDuration += t;
              return;
            case it:
              var u = a.stateNode;
              u.effectDuration += t;
              return;
          }
          a = a.return;
        }
      }
    }
    function Yg(e) {
      if (Em >= 0) {
        var t = Fo() - Em;
        Em = -1;
        for (var a = e.return; a !== null; ) {
          switch (a.tag) {
            case J:
              var i = a.stateNode;
              i !== null && (i.passiveEffectDuration += t);
              return;
            case it:
              var u = a.stateNode;
              u !== null && (u.passiveEffectDuration += t);
              return;
          }
          a = a.return;
        }
      }
    }
    function Kl() {
      Sm = Fo();
    }
    function $g() {
      Em = Fo();
    }
    function Qg(e) {
      for (var t = e.child; t; )
        e.actualDuration += t.actualDuration, t = t.sibling;
    }
    function ul(e, t) {
      if (e && e.defaultProps) {
        var a = rt({}, t), i = e.defaultProps;
        for (var u in i)
          a[u] === void 0 && (a[u] = i[u]);
        return a;
      }
      return t;
    }
    var Wg = {}, Gg, Kg, qg, Xg, Zg, ZC, Tm, Jg, eS, tS, Dp;
    {
      Gg = /* @__PURE__ */ new Set(), Kg = /* @__PURE__ */ new Set(), qg = /* @__PURE__ */ new Set(), Xg = /* @__PURE__ */ new Set(), Jg = /* @__PURE__ */ new Set(), Zg = /* @__PURE__ */ new Set(), eS = /* @__PURE__ */ new Set(), tS = /* @__PURE__ */ new Set(), Dp = /* @__PURE__ */ new Set();
      var JC = /* @__PURE__ */ new Set();
      Tm = function(e, t) {
        if (!(e === null || typeof e == "function")) {
          var a = t + "_" + e;
          JC.has(a) || (JC.add(a), S("%s(...): Expected the last optional `callback` argument to be a function. Instead received: %s.", t, e));
        }
      }, ZC = function(e, t) {
        if (t === void 0) {
          var a = xt(e) || "Component";
          Zg.has(a) || (Zg.add(a), S("%s.getDerivedStateFromProps(): A valid state object (or null) must be returned. You have returned undefined.", a));
        }
      }, Object.defineProperty(Wg, "_processChildContext", {
        enumerable: !1,
        value: function() {
          throw new Error("_processChildContext is not available in React 16+. This likely means you have multiple copies of React and are attempting to nest a React 15 tree inside a React 16 tree using unstable_renderSubtreeIntoContainer, which isn't supported. Try to make sure you have only one copy of React (and ideally, switch to ReactDOM.createPortal).");
        }
      }), Object.freeze(Wg);
    }
    function nS(e, t, a, i) {
      var u = e.memoizedState, s = a(i, u);
      {
        if (e.mode & Kt) {
          yn(!0);
          try {
            s = a(i, u);
          } finally {
            yn(!1);
          }
        }
        ZC(t, s);
      }
      var f = s == null ? u : rt({}, u, s);
      if (e.memoizedState = f, e.lanes === $) {
        var p = e.updateQueue;
        p.baseState = f;
      }
    }
    var rS = {
      isMounted: Ov,
      enqueueSetState: function(e, t, a) {
        var i = po(e), u = Ea(), s = Bo(i), f = Pu(u, s);
        f.payload = t, a != null && (Tm(a, "setState"), f.callback = a);
        var p = zo(i, f, s);
        p !== null && (yr(p, i, s, u), Zh(p, i, s)), vs(i, s);
      },
      enqueueReplaceState: function(e, t, a) {
        var i = po(e), u = Ea(), s = Bo(i), f = Pu(u, s);
        f.tag = mC, f.payload = t, a != null && (Tm(a, "replaceState"), f.callback = a);
        var p = zo(i, f, s);
        p !== null && (yr(p, i, s, u), Zh(p, i, s)), vs(i, s);
      },
      enqueueForceUpdate: function(e, t) {
        var a = po(e), i = Ea(), u = Bo(a), s = Pu(i, u);
        s.tag = Kh, t != null && (Tm(t, "forceUpdate"), s.callback = t);
        var f = zo(a, s, u);
        f !== null && (yr(f, a, u, i), Zh(f, a, u)), Mc(a, u);
      }
    };
    function e0(e, t, a, i, u, s, f) {
      var p = e.stateNode;
      if (typeof p.shouldComponentUpdate == "function") {
        var v = p.shouldComponentUpdate(i, s, f);
        {
          if (e.mode & Kt) {
            yn(!0);
            try {
              v = p.shouldComponentUpdate(i, s, f);
            } finally {
              yn(!1);
            }
          }
          v === void 0 && S("%s.shouldComponentUpdate(): Returned undefined instead of a boolean value. Make sure to return true or false.", xt(t) || "Component");
        }
        return v;
      }
      return t.prototype && t.prototype.isPureReactComponent ? !ye(a, i) || !ye(u, s) : !0;
    }
    function Gx(e, t, a) {
      var i = e.stateNode;
      {
        var u = xt(t) || "Component", s = i.render;
        s || (t.prototype && typeof t.prototype.render == "function" ? S("%s(...): No `render` method found on the returned component instance: did you accidentally return an object from the constructor?", u) : S("%s(...): No `render` method found on the returned component instance: you may have forgotten to define `render`.", u)), i.getInitialState && !i.getInitialState.isReactClassApproved && !i.state && S("getInitialState was defined on %s, a plain JavaScript class. This is only supported for classes created using React.createClass. Did you mean to define a state property instead?", u), i.getDefaultProps && !i.getDefaultProps.isReactClassApproved && S("getDefaultProps was defined on %s, a plain JavaScript class. This is only supported for classes created using React.createClass. Use a static property to define defaultProps instead.", u), i.propTypes && S("propTypes was defined as an instance property on %s. Use a static property to define propTypes instead.", u), i.contextType && S("contextType was defined as an instance property on %s. Use a static property to define contextType instead.", u), t.childContextTypes && !Dp.has(t) && // Strict Mode has its own warning for legacy context, so we can skip
        // this one.
        (e.mode & Kt) === Oe && (Dp.add(t), S(`%s uses the legacy childContextTypes API which is no longer supported and will be removed in the next major release. Use React.createContext() instead

.Learn more about this warning here: https://reactjs.org/link/legacy-context`, u)), t.contextTypes && !Dp.has(t) && // Strict Mode has its own warning for legacy context, so we can skip
        // this one.
        (e.mode & Kt) === Oe && (Dp.add(t), S(`%s uses the legacy contextTypes API which is no longer supported and will be removed in the next major release. Use React.createContext() with static contextType instead.

Learn more about this warning here: https://reactjs.org/link/legacy-context`, u)), i.contextTypes && S("contextTypes was defined as an instance property on %s. Use a static property to define contextTypes instead.", u), t.contextType && t.contextTypes && !eS.has(t) && (eS.add(t), S("%s declares both contextTypes and contextType static properties. The legacy contextTypes property will be ignored.", u)), typeof i.componentShouldUpdate == "function" && S("%s has a method called componentShouldUpdate(). Did you mean shouldComponentUpdate()? The name is phrased as a question because the function is expected to return a value.", u), t.prototype && t.prototype.isPureReactComponent && typeof i.shouldComponentUpdate < "u" && S("%s has a method called shouldComponentUpdate(). shouldComponentUpdate should not be used when extending React.PureComponent. Please extend React.Component if shouldComponentUpdate is used.", xt(t) || "A pure component"), typeof i.componentDidUnmount == "function" && S("%s has a method called componentDidUnmount(). But there is no such lifecycle method. Did you mean componentWillUnmount()?", u), typeof i.componentDidReceiveProps == "function" && S("%s has a method called componentDidReceiveProps(). But there is no such lifecycle method. If you meant to update the state in response to changing props, use componentWillReceiveProps(). If you meant to fetch data or run side-effects or mutations after React has updated the UI, use componentDidUpdate().", u), typeof i.componentWillRecieveProps == "function" && S("%s has a method called componentWillRecieveProps(). Did you mean componentWillReceiveProps()?", u), typeof i.UNSAFE_componentWillRecieveProps == "function" && S("%s has a method called UNSAFE_componentWillRecieveProps(). Did you mean UNSAFE_componentWillReceiveProps()?", u);
        var f = i.props !== a;
        i.props !== void 0 && f && S("%s(...): When calling super() in `%s`, make sure to pass up the same props that your component's constructor was passed.", u, u), i.defaultProps && S("Setting defaultProps as an instance property on %s is not supported and will be ignored. Instead, define defaultProps as a static property on %s.", u, u), typeof i.getSnapshotBeforeUpdate == "function" && typeof i.componentDidUpdate != "function" && !qg.has(t) && (qg.add(t), S("%s: getSnapshotBeforeUpdate() should be used with componentDidUpdate(). This component defines getSnapshotBeforeUpdate() only.", xt(t))), typeof i.getDerivedStateFromProps == "function" && S("%s: getDerivedStateFromProps() is defined as an instance method and will be ignored. Instead, declare it as a static method.", u), typeof i.getDerivedStateFromError == "function" && S("%s: getDerivedStateFromError() is defined as an instance method and will be ignored. Instead, declare it as a static method.", u), typeof t.getSnapshotBeforeUpdate == "function" && S("%s: getSnapshotBeforeUpdate() is defined as a static method and will be ignored. Instead, declare it as an instance method.", u);
        var p = i.state;
        p && (typeof p != "object" || st(p)) && S("%s.state: must be set to an object or null", u), typeof i.getChildContext == "function" && typeof t.childContextTypes != "object" && S("%s.getChildContext(): childContextTypes must be defined in order to use getChildContext().", u);
      }
    }
    function t0(e, t) {
      t.updater = rS, e.stateNode = t, vu(t, e), t._reactInternalInstance = Wg;
    }
    function n0(e, t, a) {
      var i = !1, u = ui, s = ui, f = t.contextType;
      if ("contextType" in t) {
        var p = (
          // Allow null for conditional declaration
          f === null || f !== void 0 && f.$$typeof === R && f._context === void 0
        );
        if (!p && !tS.has(t)) {
          tS.add(t);
          var v = "";
          f === void 0 ? v = " However, it is set to undefined. This can be caused by a typo or by mixing up named and default imports. This can also happen due to a circular dependency, so try moving the createContext() call to a separate file." : typeof f != "object" ? v = " However, it is set to a " + typeof f + "." : f.$$typeof === vi ? v = " Did you accidentally pass the Context.Provider instead?" : f._context !== void 0 ? v = " Did you accidentally pass the Context.Consumer instead?" : v = " However, it is set to an object with keys {" + Object.keys(f).join(", ") + "}.", S("%s defines an invalid contextType. contextType should point to the Context object returned by React.createContext().%s", xt(t) || "Component", v);
        }
      }
      if (typeof f == "object" && f !== null)
        s = tr(f);
      else {
        u = Rf(e, t, !0);
        var y = t.contextTypes;
        i = y != null, s = i ? Tf(e, u) : ui;
      }
      var g = new t(a, s);
      if (e.mode & Kt) {
        yn(!0);
        try {
          g = new t(a, s);
        } finally {
          yn(!1);
        }
      }
      var b = e.memoizedState = g.state !== null && g.state !== void 0 ? g.state : null;
      t0(e, g);
      {
        if (typeof t.getDerivedStateFromProps == "function" && b === null) {
          var w = xt(t) || "Component";
          Kg.has(w) || (Kg.add(w), S("`%s` uses `getDerivedStateFromProps` but its initial state is %s. This is not recommended. Instead, define the initial state by assigning an object to `this.state` in the constructor of `%s`. This ensures that `getDerivedStateFromProps` arguments have a consistent shape.", w, g.state === null ? "null" : "undefined", w));
        }
        if (typeof t.getDerivedStateFromProps == "function" || typeof g.getSnapshotBeforeUpdate == "function") {
          var N = null, A = null, H = null;
          if (typeof g.componentWillMount == "function" && g.componentWillMount.__suppressDeprecationWarning !== !0 ? N = "componentWillMount" : typeof g.UNSAFE_componentWillMount == "function" && (N = "UNSAFE_componentWillMount"), typeof g.componentWillReceiveProps == "function" && g.componentWillReceiveProps.__suppressDeprecationWarning !== !0 ? A = "componentWillReceiveProps" : typeof g.UNSAFE_componentWillReceiveProps == "function" && (A = "UNSAFE_componentWillReceiveProps"), typeof g.componentWillUpdate == "function" && g.componentWillUpdate.__suppressDeprecationWarning !== !0 ? H = "componentWillUpdate" : typeof g.UNSAFE_componentWillUpdate == "function" && (H = "UNSAFE_componentWillUpdate"), N !== null || A !== null || H !== null) {
            var ue = xt(t) || "Component", ze = typeof t.getDerivedStateFromProps == "function" ? "getDerivedStateFromProps()" : "getSnapshotBeforeUpdate()";
            Xg.has(ue) || (Xg.add(ue), S(`Unsafe legacy lifecycles will not be called for components using new component APIs.

%s uses %s but also contains the following legacy lifecycles:%s%s%s

The above lifecycles should be removed. Learn more about this warning here:
https://reactjs.org/link/unsafe-component-lifecycles`, ue, ze, N !== null ? `
  ` + N : "", A !== null ? `
  ` + A : "", H !== null ? `
  ` + H : ""));
          }
        }
      }
      return i && $E(e, u, s), g;
    }
    function Kx(e, t) {
      var a = t.state;
      typeof t.componentWillMount == "function" && t.componentWillMount(), typeof t.UNSAFE_componentWillMount == "function" && t.UNSAFE_componentWillMount(), a !== t.state && (S("%s.componentWillMount(): Assigning directly to this.state is deprecated (except inside a component's constructor). Use setState instead.", We(e) || "Component"), rS.enqueueReplaceState(t, t.state, null));
    }
    function r0(e, t, a, i) {
      var u = t.state;
      if (typeof t.componentWillReceiveProps == "function" && t.componentWillReceiveProps(a, i), typeof t.UNSAFE_componentWillReceiveProps == "function" && t.UNSAFE_componentWillReceiveProps(a, i), t.state !== u) {
        {
          var s = We(e) || "Component";
          Gg.has(s) || (Gg.add(s), S("%s.componentWillReceiveProps(): Assigning directly to this.state is deprecated (except inside a component's constructor). Use setState instead.", s));
        }
        rS.enqueueReplaceState(t, t.state, null);
      }
    }
    function aS(e, t, a, i) {
      Gx(e, t, a);
      var u = e.stateNode;
      u.props = a, u.state = e.memoizedState, u.refs = {}, pg(e);
      var s = t.contextType;
      if (typeof s == "object" && s !== null)
        u.context = tr(s);
      else {
        var f = Rf(e, t, !0);
        u.context = Tf(e, f);
      }
      {
        if (u.state === a) {
          var p = xt(t) || "Component";
          Jg.has(p) || (Jg.add(p), S("%s: It is not recommended to assign props directly to state because updates to props won't be reflected in state. In most cases, it is better to use props directly.", p));
        }
        e.mode & Kt && al.recordLegacyContextWarning(e, u), al.recordUnsafeLifecycleWarnings(e, u);
      }
      u.state = e.memoizedState;
      var v = t.getDerivedStateFromProps;
      if (typeof v == "function" && (nS(e, t, v, a), u.state = e.memoizedState), typeof t.getDerivedStateFromProps != "function" && typeof u.getSnapshotBeforeUpdate != "function" && (typeof u.UNSAFE_componentWillMount == "function" || typeof u.componentWillMount == "function") && (Kx(e, u), Jh(e, a, u, i), u.state = e.memoizedState), typeof u.componentDidMount == "function") {
        var y = Ct;
        y |= Wi, (e.mode & Nt) !== Oe && (y |= _l), e.flags |= y;
      }
    }
    function qx(e, t, a, i) {
      var u = e.stateNode, s = e.memoizedProps;
      u.props = s;
      var f = u.context, p = t.contextType, v = ui;
      if (typeof p == "object" && p !== null)
        v = tr(p);
      else {
        var y = Rf(e, t, !0);
        v = Tf(e, y);
      }
      var g = t.getDerivedStateFromProps, b = typeof g == "function" || typeof u.getSnapshotBeforeUpdate == "function";
      !b && (typeof u.UNSAFE_componentWillReceiveProps == "function" || typeof u.componentWillReceiveProps == "function") && (s !== a || f !== v) && r0(e, u, a, v), gC();
      var w = e.memoizedState, N = u.state = w;
      if (Jh(e, a, u, i), N = e.memoizedState, s === a && w === N && !zh() && !em()) {
        if (typeof u.componentDidMount == "function") {
          var A = Ct;
          A |= Wi, (e.mode & Nt) !== Oe && (A |= _l), e.flags |= A;
        }
        return !1;
      }
      typeof g == "function" && (nS(e, t, g, a), N = e.memoizedState);
      var H = em() || e0(e, t, s, a, w, N, v);
      if (H) {
        if (!b && (typeof u.UNSAFE_componentWillMount == "function" || typeof u.componentWillMount == "function") && (typeof u.componentWillMount == "function" && u.componentWillMount(), typeof u.UNSAFE_componentWillMount == "function" && u.UNSAFE_componentWillMount()), typeof u.componentDidMount == "function") {
          var ue = Ct;
          ue |= Wi, (e.mode & Nt) !== Oe && (ue |= _l), e.flags |= ue;
        }
      } else {
        if (typeof u.componentDidMount == "function") {
          var ze = Ct;
          ze |= Wi, (e.mode & Nt) !== Oe && (ze |= _l), e.flags |= ze;
        }
        e.memoizedProps = a, e.memoizedState = N;
      }
      return u.props = a, u.state = N, u.context = v, H;
    }
    function Xx(e, t, a, i, u) {
      var s = t.stateNode;
      yC(e, t);
      var f = t.memoizedProps, p = t.type === t.elementType ? f : ul(t.type, f);
      s.props = p;
      var v = t.pendingProps, y = s.context, g = a.contextType, b = ui;
      if (typeof g == "object" && g !== null)
        b = tr(g);
      else {
        var w = Rf(t, a, !0);
        b = Tf(t, w);
      }
      var N = a.getDerivedStateFromProps, A = typeof N == "function" || typeof s.getSnapshotBeforeUpdate == "function";
      !A && (typeof s.UNSAFE_componentWillReceiveProps == "function" || typeof s.componentWillReceiveProps == "function") && (f !== v || y !== b) && r0(t, s, i, b), gC();
      var H = t.memoizedState, ue = s.state = H;
      if (Jh(t, i, s, u), ue = t.memoizedState, f === v && H === ue && !zh() && !em() && !we)
        return typeof s.componentDidUpdate == "function" && (f !== e.memoizedProps || H !== e.memoizedState) && (t.flags |= Ct), typeof s.getSnapshotBeforeUpdate == "function" && (f !== e.memoizedProps || H !== e.memoizedState) && (t.flags |= $n), !1;
      typeof N == "function" && (nS(t, a, N, i), ue = t.memoizedState);
      var ze = em() || e0(t, a, p, i, H, ue, b) || // TODO: In some cases, we'll end up checking if context has changed twice,
      // both before and after `shouldComponentUpdate` has been called. Not ideal,
      // but I'm loath to refactor this function. This only happens for memoized
      // components so it's not that common.
      we;
      return ze ? (!A && (typeof s.UNSAFE_componentWillUpdate == "function" || typeof s.componentWillUpdate == "function") && (typeof s.componentWillUpdate == "function" && s.componentWillUpdate(i, ue, b), typeof s.UNSAFE_componentWillUpdate == "function" && s.UNSAFE_componentWillUpdate(i, ue, b)), typeof s.componentDidUpdate == "function" && (t.flags |= Ct), typeof s.getSnapshotBeforeUpdate == "function" && (t.flags |= $n)) : (typeof s.componentDidUpdate == "function" && (f !== e.memoizedProps || H !== e.memoizedState) && (t.flags |= Ct), typeof s.getSnapshotBeforeUpdate == "function" && (f !== e.memoizedProps || H !== e.memoizedState) && (t.flags |= $n), t.memoizedProps = i, t.memoizedState = ue), s.props = i, s.state = ue, s.context = b, ze;
    }
    function Js(e, t) {
      return {
        value: e,
        source: t,
        stack: Vi(t),
        digest: null
      };
    }
    function iS(e, t, a) {
      return {
        value: e,
        source: null,
        stack: a ?? null,
        digest: t ?? null
      };
    }
    function Zx(e, t) {
      return !0;
    }
    function lS(e, t) {
      try {
        var a = Zx(e, t);
        if (a === !1)
          return;
        var i = t.value, u = t.source, s = t.stack, f = s !== null ? s : "";
        if (i != null && i._suppressLogging) {
          if (e.tag === ce)
            return;
          console.error(i);
        }
        var p = u ? We(u) : null, v = p ? "The above error occurred in the <" + p + "> component:" : "The above error occurred in one of your React components:", y;
        if (e.tag === J)
          y = `Consider adding an error boundary to your tree to customize error handling behavior.
Visit https://reactjs.org/link/error-boundaries to learn more about error boundaries.`;
        else {
          var g = We(e) || "Anonymous";
          y = "React will try to recreate this component tree from scratch " + ("using the error boundary you provided, " + g + ".");
        }
        var b = v + `
` + f + `

` + ("" + y);
        console.error(b);
      } catch (w) {
        setTimeout(function() {
          throw w;
        });
      }
    }
    var Jx = typeof WeakMap == "function" ? WeakMap : Map;
    function a0(e, t, a) {
      var i = Pu(Zt, a);
      i.tag = fg, i.payload = {
        element: null
      };
      var u = t.value;
      return i.callback = function() {
        $1(u), lS(e, t);
      }, i;
    }
    function uS(e, t, a) {
      var i = Pu(Zt, a);
      i.tag = fg;
      var u = e.type.getDerivedStateFromError;
      if (typeof u == "function") {
        var s = t.value;
        i.payload = function() {
          return u(s);
        }, i.callback = function() {
          hR(e), lS(e, t);
        };
      }
      var f = e.stateNode;
      return f !== null && typeof f.componentDidCatch == "function" && (i.callback = function() {
        hR(e), lS(e, t), typeof u != "function" && I1(this);
        var v = t.value, y = t.stack;
        this.componentDidCatch(v, {
          componentStack: y !== null ? y : ""
        }), typeof u != "function" && (Jr(e.lanes, Be) || S("%s: Error boundaries should implement getDerivedStateFromError(). In that method, return a state update to display an error message or fallback UI.", We(e) || "Unknown"));
      }), i;
    }
    function i0(e, t, a) {
      var i = e.pingCache, u;
      if (i === null ? (i = e.pingCache = new Jx(), u = /* @__PURE__ */ new Set(), i.set(t, u)) : (u = i.get(t), u === void 0 && (u = /* @__PURE__ */ new Set(), i.set(t, u))), !u.has(a)) {
        u.add(a);
        var s = Q1.bind(null, e, t, a);
        Xr && Qp(e, a), t.then(s, s);
      }
    }
    function eb(e, t, a, i) {
      var u = e.updateQueue;
      if (u === null) {
        var s = /* @__PURE__ */ new Set();
        s.add(a), e.updateQueue = s;
      } else
        u.add(a);
    }
    function tb(e, t) {
      var a = e.tag;
      if ((e.mode & vt) === Oe && (a === se || a === Le || a === He)) {
        var i = e.alternate;
        i ? (e.updateQueue = i.updateQueue, e.memoizedState = i.memoizedState, e.lanes = i.lanes) : (e.updateQueue = null, e.memoizedState = null);
      }
    }
    function l0(e) {
      var t = e;
      do {
        if (t.tag === ke && Ux(t))
          return t;
        t = t.return;
      } while (t !== null);
      return null;
    }
    function u0(e, t, a, i, u) {
      if ((e.mode & vt) === Oe) {
        if (e === t)
          e.flags |= Xn;
        else {
          if (e.flags |= _e, a.flags |= wc, a.flags &= -52805, a.tag === ce) {
            var s = a.alternate;
            if (s === null)
              a.tag = Pt;
            else {
              var f = Pu(Zt, Be);
              f.tag = Kh, zo(a, f, Be);
            }
          }
          a.lanes = et(a.lanes, Be);
        }
        return e;
      }
      return e.flags |= Xn, e.lanes = u, e;
    }
    function nb(e, t, a, i, u) {
      if (a.flags |= os, Xr && Qp(e, u), i !== null && typeof i == "object" && typeof i.then == "function") {
        var s = i;
        tb(a), Ar() && a.mode & vt && ZE();
        var f = l0(t);
        if (f !== null) {
          f.flags &= ~Cr, u0(f, t, a, e, u), f.mode & vt && i0(e, s, u), eb(f, e, s);
          return;
        } else {
          if (!Fv(u)) {
            i0(e, s, u), PS();
            return;
          }
          var p = new Error("A component suspended while responding to synchronous input. This will cause the UI to be replaced with a loading indicator. To fix, updates that suspend should be wrapped with startTransition.");
          i = p;
        }
      } else if (Ar() && a.mode & vt) {
        ZE();
        var v = l0(t);
        if (v !== null) {
          (v.flags & Xn) === De && (v.flags |= Cr), u0(v, t, a, e, u), Jy(Js(i, a));
          return;
        }
      }
      i = Js(i, a), U1(i);
      var y = t;
      do {
        switch (y.tag) {
          case J: {
            var g = i;
            y.flags |= Xn;
            var b = Ts(u);
            y.lanes = et(y.lanes, b);
            var w = a0(y, g, b);
            vg(y, w);
            return;
          }
          case ce:
            var N = i, A = y.type, H = y.stateNode;
            if ((y.flags & _e) === De && (typeof A.getDerivedStateFromError == "function" || H !== null && typeof H.componentDidCatch == "function" && !lR(H))) {
              y.flags |= Xn;
              var ue = Ts(u);
              y.lanes = et(y.lanes, ue);
              var ze = uS(y, N, ue);
              vg(y, ze);
              return;
            }
            break;
        }
        y = y.return;
      } while (y !== null);
    }
    function rb() {
      return null;
    }
    var Op = k.ReactCurrentOwner, ol = !1, oS, Lp, sS, cS, fS, ec, dS, wm, Mp;
    oS = {}, Lp = {}, sS = {}, cS = {}, fS = {}, ec = !1, dS = {}, wm = {}, Mp = {};
    function ga(e, t, a, i) {
      e === null ? t.child = cC(t, null, a, i) : t.child = _f(t, e.child, a, i);
    }
    function ab(e, t, a, i) {
      t.child = _f(t, e.child, null, i), t.child = _f(t, null, a, i);
    }
    function o0(e, t, a, i, u) {
      if (t.type !== t.elementType) {
        var s = a.propTypes;
        s && nl(
          s,
          i,
          // Resolved props
          "prop",
          xt(a)
        );
      }
      var f = a.render, p = t.ref, v, y;
      Df(t, u), va(t);
      {
        if (Op.current = t, Yn(!0), v = Uf(e, t, f, i, p, u), y = Af(), t.mode & Kt) {
          yn(!0);
          try {
            v = Uf(e, t, f, i, p, u), y = Af();
          } finally {
            yn(!1);
          }
        }
        Yn(!1);
      }
      return ha(), e !== null && !ol ? (wC(e, t, u), Vu(e, t, u)) : (Ar() && y && Wy(t), t.flags |= ni, ga(e, t, v, u), t.child);
    }
    function s0(e, t, a, i, u) {
      if (e === null) {
        var s = a.type;
        if (s_(s) && a.compare === null && // SimpleMemoComponent codepath doesn't resolve outer props either.
        a.defaultProps === void 0) {
          var f = s;
          return f = Yf(s), t.tag = He, t.type = f, hS(t, s), c0(e, t, f, i, u);
        }
        {
          var p = s.propTypes;
          if (p && nl(
            p,
            i,
            // Resolved props
            "prop",
            xt(s)
          ), a.defaultProps !== void 0) {
            var v = xt(s) || "Unknown";
            Mp[v] || (S("%s: Support for defaultProps will be removed from memo components in a future major release. Use JavaScript default parameters instead.", v), Mp[v] = !0);
          }
        }
        var y = XS(a.type, null, i, t, t.mode, u);
        return y.ref = t.ref, y.return = t, t.child = y, y;
      }
      {
        var g = a.type, b = g.propTypes;
        b && nl(
          b,
          i,
          // Resolved props
          "prop",
          xt(g)
        );
      }
      var w = e.child, N = CS(e, u);
      if (!N) {
        var A = w.memoizedProps, H = a.compare;
        if (H = H !== null ? H : ye, H(A, i) && e.ref === t.ref)
          return Vu(e, t, u);
      }
      t.flags |= ni;
      var ue = ic(w, i);
      return ue.ref = t.ref, ue.return = t, t.child = ue, ue;
    }
    function c0(e, t, a, i, u) {
      if (t.type !== t.elementType) {
        var s = t.elementType;
        if (s.$$typeof === Ge) {
          var f = s, p = f._payload, v = f._init;
          try {
            s = v(p);
          } catch {
            s = null;
          }
          var y = s && s.propTypes;
          y && nl(
            y,
            i,
            // Resolved (SimpleMemoComponent has no defaultProps)
            "prop",
            xt(s)
          );
        }
      }
      if (e !== null) {
        var g = e.memoizedProps;
        if (ye(g, i) && e.ref === t.ref && // Prevent bailout if the implementation changed due to hot reload.
        t.type === e.type)
          if (ol = !1, t.pendingProps = i = g, CS(e, u))
            (e.flags & wc) !== De && (ol = !0);
          else return t.lanes = e.lanes, Vu(e, t, u);
      }
      return pS(e, t, a, i, u);
    }
    function f0(e, t, a) {
      var i = t.pendingProps, u = i.children, s = e !== null ? e.memoizedState : null;
      if (i.mode === "hidden" || ne)
        if ((t.mode & vt) === Oe) {
          var f = {
            baseLanes: $,
            cachePool: null,
            transitions: null
          };
          t.memoizedState = f, jm(t, a);
        } else if (Jr(a, Zr)) {
          var b = {
            baseLanes: $,
            cachePool: null,
            transitions: null
          };
          t.memoizedState = b;
          var w = s !== null ? s.baseLanes : a;
          jm(t, w);
        } else {
          var p = null, v;
          if (s !== null) {
            var y = s.baseLanes;
            v = et(y, a);
          } else
            v = a;
          t.lanes = t.childLanes = Zr;
          var g = {
            baseLanes: v,
            cachePool: p,
            transitions: null
          };
          return t.memoizedState = g, t.updateQueue = null, jm(t, v), null;
        }
      else {
        var N;
        s !== null ? (N = et(s.baseLanes, a), t.memoizedState = null) : N = a, jm(t, N);
      }
      return ga(e, t, u, a), t.child;
    }
    function ib(e, t, a) {
      var i = t.pendingProps;
      return ga(e, t, i, a), t.child;
    }
    function lb(e, t, a) {
      var i = t.pendingProps.children;
      return ga(e, t, i, a), t.child;
    }
    function ub(e, t, a) {
      {
        t.flags |= Ct;
        {
          var i = t.stateNode;
          i.effectDuration = 0, i.passiveEffectDuration = 0;
        }
      }
      var u = t.pendingProps, s = u.children;
      return ga(e, t, s, a), t.child;
    }
    function d0(e, t) {
      var a = t.ref;
      (e === null && a !== null || e !== null && e.ref !== a) && (t.flags |= En, t.flags |= ho);
    }
    function pS(e, t, a, i, u) {
      if (t.type !== t.elementType) {
        var s = a.propTypes;
        s && nl(
          s,
          i,
          // Resolved props
          "prop",
          xt(a)
        );
      }
      var f;
      {
        var p = Rf(t, a, !0);
        f = Tf(t, p);
      }
      var v, y;
      Df(t, u), va(t);
      {
        if (Op.current = t, Yn(!0), v = Uf(e, t, a, i, f, u), y = Af(), t.mode & Kt) {
          yn(!0);
          try {
            v = Uf(e, t, a, i, f, u), y = Af();
          } finally {
            yn(!1);
          }
        }
        Yn(!1);
      }
      return ha(), e !== null && !ol ? (wC(e, t, u), Vu(e, t, u)) : (Ar() && y && Wy(t), t.flags |= ni, ga(e, t, v, u), t.child);
    }
    function p0(e, t, a, i, u) {
      {
        switch (w_(t)) {
          case !1: {
            var s = t.stateNode, f = t.type, p = new f(t.memoizedProps, s.context), v = p.state;
            s.updater.enqueueSetState(s, v, null);
            break;
          }
          case !0: {
            t.flags |= _e, t.flags |= Xn;
            var y = new Error("Simulated error coming from DevTools"), g = Ts(u);
            t.lanes = et(t.lanes, g);
            var b = uS(t, Js(y, t), g);
            vg(t, b);
            break;
          }
        }
        if (t.type !== t.elementType) {
          var w = a.propTypes;
          w && nl(
            w,
            i,
            // Resolved props
            "prop",
            xt(a)
          );
        }
      }
      var N;
      Yl(a) ? (N = !0, Ah(t)) : N = !1, Df(t, u);
      var A = t.stateNode, H;
      A === null ? (bm(e, t), n0(t, a, i), aS(t, a, i, u), H = !0) : e === null ? H = qx(t, a, i, u) : H = Xx(e, t, a, i, u);
      var ue = vS(e, t, a, H, N, u);
      {
        var ze = t.stateNode;
        H && ze.props !== i && (ec || S("It looks like %s is reassigning its own `this.props` while rendering. This is not supported and can lead to confusing bugs.", We(t) || "a component"), ec = !0);
      }
      return ue;
    }
    function vS(e, t, a, i, u, s) {
      d0(e, t);
      var f = (t.flags & _e) !== De;
      if (!i && !f)
        return u && GE(t, a, !1), Vu(e, t, s);
      var p = t.stateNode;
      Op.current = t;
      var v;
      if (f && typeof a.getDerivedStateFromError != "function")
        v = null, XC();
      else {
        va(t);
        {
          if (Yn(!0), v = p.render(), t.mode & Kt) {
            yn(!0);
            try {
              p.render();
            } finally {
              yn(!1);
            }
          }
          Yn(!1);
        }
        ha();
      }
      return t.flags |= ni, e !== null && f ? ab(e, t, v, s) : ga(e, t, v, s), t.memoizedState = p.state, u && GE(t, a, !0), t.child;
    }
    function v0(e) {
      var t = e.stateNode;
      t.pendingContext ? QE(e, t.pendingContext, t.pendingContext !== t.context) : t.context && QE(e, t.context, !1), hg(e, t.containerInfo);
    }
    function ob(e, t, a) {
      if (v0(t), e === null)
        throw new Error("Should have a current fiber. This is a bug in React.");
      var i = t.pendingProps, u = t.memoizedState, s = u.element;
      yC(e, t), Jh(t, i, null, a);
      var f = t.memoizedState;
      t.stateNode;
      var p = f.element;
      if (u.isDehydrated) {
        var v = {
          element: p,
          isDehydrated: !1,
          cache: f.cache,
          pendingSuspenseBoundaries: f.pendingSuspenseBoundaries,
          transitions: f.transitions
        }, y = t.updateQueue;
        if (y.baseState = v, t.memoizedState = v, t.flags & Cr) {
          var g = Js(new Error("There was an error while hydrating. Because the error happened outside of a Suspense boundary, the entire root will switch to client rendering."), t);
          return h0(e, t, p, a, g);
        } else if (p !== s) {
          var b = Js(new Error("This root received an early update, before anything was able hydrate. Switched the entire root to client rendering."), t);
          return h0(e, t, p, a, b);
        } else {
          fx(t);
          var w = cC(t, null, p, a);
          t.child = w;
          for (var N = w; N; )
            N.flags = N.flags & ~mn | Gr, N = N.sibling;
        }
      } else {
        if (bf(), p === s)
          return Vu(e, t, a);
        ga(e, t, p, a);
      }
      return t.child;
    }
    function h0(e, t, a, i, u) {
      return bf(), Jy(u), t.flags |= Cr, ga(e, t, a, i), t.child;
    }
    function sb(e, t, a) {
      CC(t), e === null && Zy(t);
      var i = t.type, u = t.pendingProps, s = e !== null ? e.memoizedProps : null, f = u.children, p = Ny(i, u);
      return p ? f = null : s !== null && Ny(i, s) && (t.flags |= Da), d0(e, t), ga(e, t, f, a), t.child;
    }
    function cb(e, t) {
      return e === null && Zy(t), null;
    }
    function fb(e, t, a, i) {
      bm(e, t);
      var u = t.pendingProps, s = a, f = s._payload, p = s._init, v = p(f);
      t.type = v;
      var y = t.tag = c_(v), g = ul(v, u), b;
      switch (y) {
        case se:
          return hS(t, v), t.type = v = Yf(v), b = pS(null, t, v, g, i), b;
        case ce:
          return t.type = v = $S(v), b = p0(null, t, v, g, i), b;
        case Le:
          return t.type = v = QS(v), b = o0(null, t, v, g, i), b;
        case Qe: {
          if (t.type !== t.elementType) {
            var w = v.propTypes;
            w && nl(
              w,
              g,
              // Resolved for outer only
              "prop",
              xt(v)
            );
          }
          return b = s0(
            null,
            t,
            v,
            ul(v.type, g),
            // The inner type can have defaults too
            i
          ), b;
        }
      }
      var N = "";
      throw v !== null && typeof v == "object" && v.$$typeof === Ge && (N = " Did you wrap a component in React.lazy() more than once?"), new Error("Element type is invalid. Received a promise that resolves to: " + v + ". " + ("Lazy element type must resolve to a class or function." + N));
    }
    function db(e, t, a, i, u) {
      bm(e, t), t.tag = ce;
      var s;
      return Yl(a) ? (s = !0, Ah(t)) : s = !1, Df(t, u), n0(t, a, i), aS(t, a, i, u), vS(null, t, a, !0, s, u);
    }
    function pb(e, t, a, i) {
      bm(e, t);
      var u = t.pendingProps, s;
      {
        var f = Rf(t, a, !1);
        s = Tf(t, f);
      }
      Df(t, i);
      var p, v;
      va(t);
      {
        if (a.prototype && typeof a.prototype.render == "function") {
          var y = xt(a) || "Unknown";
          oS[y] || (S("The <%s /> component appears to have a render method, but doesn't extend React.Component. This is likely to cause errors. Change %s to extend React.Component instead.", y, y), oS[y] = !0);
        }
        t.mode & Kt && al.recordLegacyContextWarning(t, null), Yn(!0), Op.current = t, p = Uf(null, t, a, u, s, i), v = Af(), Yn(!1);
      }
      if (ha(), t.flags |= ni, typeof p == "object" && p !== null && typeof p.render == "function" && p.$$typeof === void 0) {
        var g = xt(a) || "Unknown";
        Lp[g] || (S("The <%s /> component appears to be a function component that returns a class instance. Change %s to a class that extends React.Component instead. If you can't use a class try assigning the prototype on the function as a workaround. `%s.prototype = React.Component.prototype`. Don't use an arrow function since it cannot be called with `new` by React.", g, g, g), Lp[g] = !0);
      }
      if (
        // Run these checks in production only if the flag is off.
        // Eventually we'll delete this branch altogether.
        typeof p == "object" && p !== null && typeof p.render == "function" && p.$$typeof === void 0
      ) {
        {
          var b = xt(a) || "Unknown";
          Lp[b] || (S("The <%s /> component appears to be a function component that returns a class instance. Change %s to a class that extends React.Component instead. If you can't use a class try assigning the prototype on the function as a workaround. `%s.prototype = React.Component.prototype`. Don't use an arrow function since it cannot be called with `new` by React.", b, b, b), Lp[b] = !0);
        }
        t.tag = ce, t.memoizedState = null, t.updateQueue = null;
        var w = !1;
        return Yl(a) ? (w = !0, Ah(t)) : w = !1, t.memoizedState = p.state !== null && p.state !== void 0 ? p.state : null, pg(t), t0(t, p), aS(t, a, u, i), vS(null, t, a, !0, w, i);
      } else {
        if (t.tag = se, t.mode & Kt) {
          yn(!0);
          try {
            p = Uf(null, t, a, u, s, i), v = Af();
          } finally {
            yn(!1);
          }
        }
        return Ar() && v && Wy(t), ga(null, t, p, i), hS(t, a), t.child;
      }
    }
    function hS(e, t) {
      {
        if (t && t.childContextTypes && S("%s(...): childContextTypes cannot be defined on a function component.", t.displayName || t.name || "Component"), e.ref !== null) {
          var a = "", i = Dr();
          i && (a += `

Check the render method of \`` + i + "`.");
          var u = i || "", s = e._debugSource;
          s && (u = s.fileName + ":" + s.lineNumber), fS[u] || (fS[u] = !0, S("Function components cannot be given refs. Attempts to access this ref will fail. Did you mean to use React.forwardRef()?%s", a));
        }
        if (t.defaultProps !== void 0) {
          var f = xt(t) || "Unknown";
          Mp[f] || (S("%s: Support for defaultProps will be removed from function components in a future major release. Use JavaScript default parameters instead.", f), Mp[f] = !0);
        }
        if (typeof t.getDerivedStateFromProps == "function") {
          var p = xt(t) || "Unknown";
          cS[p] || (S("%s: Function components do not support getDerivedStateFromProps.", p), cS[p] = !0);
        }
        if (typeof t.contextType == "object" && t.contextType !== null) {
          var v = xt(t) || "Unknown";
          sS[v] || (S("%s: Function components do not support contextType.", v), sS[v] = !0);
        }
      }
    }
    var mS = {
      dehydrated: null,
      treeContext: null,
      retryLane: Dt
    };
    function yS(e) {
      return {
        baseLanes: e,
        cachePool: rb(),
        transitions: null
      };
    }
    function vb(e, t) {
      var a = null;
      return {
        baseLanes: et(e.baseLanes, t),
        cachePool: a,
        transitions: e.transitions
      };
    }
    function hb(e, t, a, i) {
      if (t !== null) {
        var u = t.memoizedState;
        if (u === null)
          return !1;
      }
      return gg(e, Cp);
    }
    function mb(e, t) {
      return ws(e.childLanes, t);
    }
    function m0(e, t, a) {
      var i = t.pendingProps;
      x_(t) && (t.flags |= _e);
      var u = il.current, s = !1, f = (t.flags & _e) !== De;
      if (f || hb(u, e) ? (s = !0, t.flags &= ~_e) : (e === null || e.memoizedState !== null) && (u = zx(u, TC)), u = Lf(u), Ao(t, u), e === null) {
        Zy(t);
        var p = t.memoizedState;
        if (p !== null) {
          var v = p.dehydrated;
          if (v !== null)
            return Cb(t, v);
        }
        var y = i.children, g = i.fallback;
        if (s) {
          var b = yb(t, y, g, a), w = t.child;
          return w.memoizedState = yS(a), t.memoizedState = mS, b;
        } else
          return gS(t, y);
      } else {
        var N = e.memoizedState;
        if (N !== null) {
          var A = N.dehydrated;
          if (A !== null)
            return Rb(e, t, f, i, A, N, a);
        }
        if (s) {
          var H = i.fallback, ue = i.children, ze = Sb(e, t, ue, H, a), be = t.child, wt = e.child.memoizedState;
          return be.memoizedState = wt === null ? yS(a) : vb(wt, a), be.childLanes = mb(e, a), t.memoizedState = mS, ze;
        } else {
          var yt = i.children, O = gb(e, t, yt, a);
          return t.memoizedState = null, O;
        }
      }
    }
    function gS(e, t, a) {
      var i = e.mode, u = {
        mode: "visible",
        children: t
      }, s = SS(u, i);
      return s.return = e, e.child = s, s;
    }
    function yb(e, t, a, i) {
      var u = e.mode, s = e.child, f = {
        mode: "hidden",
        children: t
      }, p, v;
      return (u & vt) === Oe && s !== null ? (p = s, p.childLanes = $, p.pendingProps = f, e.mode & Mt && (p.actualDuration = 0, p.actualStartTime = -1, p.selfBaseDuration = 0, p.treeBaseDuration = 0), v = Yo(a, u, i, null)) : (p = SS(f, u), v = Yo(a, u, i, null)), p.return = e, v.return = e, p.sibling = v, e.child = p, v;
    }
    function SS(e, t, a) {
      return yR(e, t, $, null);
    }
    function y0(e, t) {
      return ic(e, t);
    }
    function gb(e, t, a, i) {
      var u = e.child, s = u.sibling, f = y0(u, {
        mode: "visible",
        children: a
      });
      if ((t.mode & vt) === Oe && (f.lanes = i), f.return = t, f.sibling = null, s !== null) {
        var p = t.deletions;
        p === null ? (t.deletions = [s], t.flags |= ka) : p.push(s);
      }
      return t.child = f, f;
    }
    function Sb(e, t, a, i, u) {
      var s = t.mode, f = e.child, p = f.sibling, v = {
        mode: "hidden",
        children: a
      }, y;
      if (
        // In legacy mode, we commit the primary tree as if it successfully
        // completed, even though it's in an inconsistent state.
        (s & vt) === Oe && // Make sure we're on the second pass, i.e. the primary child fragment was
        // already cloned. In legacy mode, the only case where this isn't true is
        // when DevTools forces us to display a fallback; we skip the first render
        // pass entirely and go straight to rendering the fallback. (In Concurrent
        // Mode, SuspenseList can also trigger this scenario, but this is a legacy-
        // only codepath.)
        t.child !== f
      ) {
        var g = t.child;
        y = g, y.childLanes = $, y.pendingProps = v, t.mode & Mt && (y.actualDuration = 0, y.actualStartTime = -1, y.selfBaseDuration = f.selfBaseDuration, y.treeBaseDuration = f.treeBaseDuration), t.deletions = null;
      } else
        y = y0(f, v), y.subtreeFlags = f.subtreeFlags & zn;
      var b;
      return p !== null ? b = ic(p, i) : (b = Yo(i, s, u, null), b.flags |= mn), b.return = t, y.return = t, y.sibling = b, t.child = y, b;
    }
    function xm(e, t, a, i) {
      i !== null && Jy(i), _f(t, e.child, null, a);
      var u = t.pendingProps, s = u.children, f = gS(t, s);
      return f.flags |= mn, t.memoizedState = null, f;
    }
    function Eb(e, t, a, i, u) {
      var s = t.mode, f = {
        mode: "visible",
        children: a
      }, p = SS(f, s), v = Yo(i, s, u, null);
      return v.flags |= mn, p.return = t, v.return = t, p.sibling = v, t.child = p, (t.mode & vt) !== Oe && _f(t, e.child, null, u), v;
    }
    function Cb(e, t, a) {
      return (e.mode & vt) === Oe ? (S("Cannot hydrate Suspense in legacy mode. Switch from ReactDOM.hydrate(element, container) to ReactDOMClient.hydrateRoot(container, <App />).render(element) or remove the Suspense components from the server rendered components."), e.lanes = Be) : jy(t) ? e.lanes = Rr : e.lanes = Zr, null;
    }
    function Rb(e, t, a, i, u, s, f) {
      if (a)
        if (t.flags & Cr) {
          t.flags &= ~Cr;
          var O = iS(new Error("There was an error while hydrating this Suspense boundary. Switched to client rendering."));
          return xm(e, t, f, O);
        } else {
          if (t.memoizedState !== null)
            return t.child = e.child, t.flags |= _e, null;
          var P = i.children, L = i.fallback, q = Eb(e, t, P, L, f), pe = t.child;
          return pe.memoizedState = yS(f), t.memoizedState = mS, q;
        }
      else {
        if (sx(), (t.mode & vt) === Oe)
          return xm(
            e,
            t,
            f,
            // TODO: When we delete legacy mode, we should make this error argument
            // required — every concurrent mode path that causes hydration to
            // de-opt to client rendering should have an error message.
            null
          );
        if (jy(u)) {
          var p, v, y;
          {
            var g = bw(u);
            p = g.digest, v = g.message, y = g.stack;
          }
          var b;
          v ? b = new Error(v) : b = new Error("The server could not finish this Suspense boundary, likely due to an error during server rendering. Switched to client rendering.");
          var w = iS(b, p, y);
          return xm(e, t, f, w);
        }
        var N = Jr(f, e.childLanes);
        if (ol || N) {
          var A = Am();
          if (A !== null) {
            var H = Ud(A, f);
            if (H !== Dt && H !== s.retryLane) {
              s.retryLane = H;
              var ue = Zt;
              Fa(e, H), yr(A, e, H, ue);
            }
          }
          PS();
          var ze = iS(new Error("This Suspense boundary received an update before it finished hydrating. This caused the boundary to switch to client rendering. The usual way to fix this is to wrap the original update in startTransition."));
          return xm(e, t, f, ze);
        } else if (PE(u)) {
          t.flags |= _e, t.child = e.child;
          var be = W1.bind(null, e);
          return _w(u, be), null;
        } else {
          dx(t, u, s.treeContext);
          var wt = i.children, yt = gS(t, wt);
          return yt.flags |= Gr, yt;
        }
      }
    }
    function g0(e, t, a) {
      e.lanes = et(e.lanes, t);
      var i = e.alternate;
      i !== null && (i.lanes = et(i.lanes, t)), sg(e.return, t, a);
    }
    function Tb(e, t, a) {
      for (var i = t; i !== null; ) {
        if (i.tag === ke) {
          var u = i.memoizedState;
          u !== null && g0(i, a, e);
        } else if (i.tag === un)
          g0(i, a, e);
        else if (i.child !== null) {
          i.child.return = i, i = i.child;
          continue;
        }
        if (i === e)
          return;
        for (; i.sibling === null; ) {
          if (i.return === null || i.return === e)
            return;
          i = i.return;
        }
        i.sibling.return = i.return, i = i.sibling;
      }
    }
    function wb(e) {
      for (var t = e, a = null; t !== null; ) {
        var i = t.alternate;
        i !== null && rm(i) === null && (a = t), t = t.sibling;
      }
      return a;
    }
    function xb(e) {
      if (e !== void 0 && e !== "forwards" && e !== "backwards" && e !== "together" && !dS[e])
        if (dS[e] = !0, typeof e == "string")
          switch (e.toLowerCase()) {
            case "together":
            case "forwards":
            case "backwards": {
              S('"%s" is not a valid value for revealOrder on <SuspenseList />. Use lowercase "%s" instead.', e, e.toLowerCase());
              break;
            }
            case "forward":
            case "backward": {
              S('"%s" is not a valid value for revealOrder on <SuspenseList />. React uses the -s suffix in the spelling. Use "%ss" instead.', e, e.toLowerCase());
              break;
            }
            default:
              S('"%s" is not a supported revealOrder on <SuspenseList />. Did you mean "together", "forwards" or "backwards"?', e);
              break;
          }
        else
          S('%s is not a supported value for revealOrder on <SuspenseList />. Did you mean "together", "forwards" or "backwards"?', e);
    }
    function bb(e, t) {
      e !== void 0 && !wm[e] && (e !== "collapsed" && e !== "hidden" ? (wm[e] = !0, S('"%s" is not a supported value for tail on <SuspenseList />. Did you mean "collapsed" or "hidden"?', e)) : t !== "forwards" && t !== "backwards" && (wm[e] = !0, S('<SuspenseList tail="%s" /> is only valid if revealOrder is "forwards" or "backwards". Did you mean to specify revealOrder="forwards"?', e)));
    }
    function S0(e, t) {
      {
        var a = st(e), i = !a && typeof Je(e) == "function";
        if (a || i) {
          var u = a ? "array" : "iterable";
          return S("A nested %s was passed to row #%s in <SuspenseList />. Wrap it in an additional SuspenseList to configure its revealOrder: <SuspenseList revealOrder=...> ... <SuspenseList revealOrder=...>{%s}</SuspenseList> ... </SuspenseList>", u, t, u), !1;
        }
      }
      return !0;
    }
    function _b(e, t) {
      if ((t === "forwards" || t === "backwards") && e !== void 0 && e !== null && e !== !1)
        if (st(e)) {
          for (var a = 0; a < e.length; a++)
            if (!S0(e[a], a))
              return;
        } else {
          var i = Je(e);
          if (typeof i == "function") {
            var u = i.call(e);
            if (u)
              for (var s = u.next(), f = 0; !s.done; s = u.next()) {
                if (!S0(s.value, f))
                  return;
                f++;
              }
          } else
            S('A single row was passed to a <SuspenseList revealOrder="%s" />. This is not useful since it needs multiple rows. Did you mean to pass multiple children or an array?', t);
        }
    }
    function ES(e, t, a, i, u) {
      var s = e.memoizedState;
      s === null ? e.memoizedState = {
        isBackwards: t,
        rendering: null,
        renderingStartTime: 0,
        last: i,
        tail: a,
        tailMode: u
      } : (s.isBackwards = t, s.rendering = null, s.renderingStartTime = 0, s.last = i, s.tail = a, s.tailMode = u);
    }
    function E0(e, t, a) {
      var i = t.pendingProps, u = i.revealOrder, s = i.tail, f = i.children;
      xb(u), bb(s, u), _b(f, u), ga(e, t, f, a);
      var p = il.current, v = gg(p, Cp);
      if (v)
        p = Sg(p, Cp), t.flags |= _e;
      else {
        var y = e !== null && (e.flags & _e) !== De;
        y && Tb(t, t.child, a), p = Lf(p);
      }
      if (Ao(t, p), (t.mode & vt) === Oe)
        t.memoizedState = null;
      else
        switch (u) {
          case "forwards": {
            var g = wb(t.child), b;
            g === null ? (b = t.child, t.child = null) : (b = g.sibling, g.sibling = null), ES(
              t,
              !1,
              // isBackwards
              b,
              g,
              s
            );
            break;
          }
          case "backwards": {
            var w = null, N = t.child;
            for (t.child = null; N !== null; ) {
              var A = N.alternate;
              if (A !== null && rm(A) === null) {
                t.child = N;
                break;
              }
              var H = N.sibling;
              N.sibling = w, w = N, N = H;
            }
            ES(
              t,
              !0,
              // isBackwards
              w,
              null,
              // last
              s
            );
            break;
          }
          case "together": {
            ES(
              t,
              !1,
              // isBackwards
              null,
              // tail
              null,
              // last
              void 0
            );
            break;
          }
          default:
            t.memoizedState = null;
        }
      return t.child;
    }
    function kb(e, t, a) {
      hg(t, t.stateNode.containerInfo);
      var i = t.pendingProps;
      return e === null ? t.child = _f(t, null, i, a) : ga(e, t, i, a), t.child;
    }
    var C0 = !1;
    function Db(e, t, a) {
      var i = t.type, u = i._context, s = t.pendingProps, f = t.memoizedProps, p = s.value;
      {
        "value" in s || C0 || (C0 = !0, S("The `value` prop is required for the `<Context.Provider>`. Did you misspell it or forget to pass it?"));
        var v = t.type.propTypes;
        v && nl(v, s, "prop", "Context.Provider");
      }
      if (pC(t, u, p), f !== null) {
        var y = f.value;
        if (G(y, p)) {
          if (f.children === s.children && !zh())
            return Vu(e, t, a);
        } else
          xx(t, u, a);
      }
      var g = s.children;
      return ga(e, t, g, a), t.child;
    }
    var R0 = !1;
    function Ob(e, t, a) {
      var i = t.type;
      i._context === void 0 ? i !== i.Consumer && (R0 || (R0 = !0, S("Rendering <Context> directly is not supported and will be removed in a future major release. Did you mean to render <Context.Consumer> instead?"))) : i = i._context;
      var u = t.pendingProps, s = u.children;
      typeof s != "function" && S("A context consumer was rendered with multiple children, or a child that isn't a function. A context consumer expects a single child that is a function. If you did pass a function, make sure there is no trailing or leading whitespace around it."), Df(t, a);
      var f = tr(i);
      va(t);
      var p;
      return Op.current = t, Yn(!0), p = s(f), Yn(!1), ha(), t.flags |= ni, ga(e, t, p, a), t.child;
    }
    function Np() {
      ol = !0;
    }
    function bm(e, t) {
      (t.mode & vt) === Oe && e !== null && (e.alternate = null, t.alternate = null, t.flags |= mn);
    }
    function Vu(e, t, a) {
      return e !== null && (t.dependencies = e.dependencies), XC(), $p(t.lanes), Jr(a, t.childLanes) ? (Tx(e, t), t.child) : null;
    }
    function Lb(e, t, a) {
      {
        var i = t.return;
        if (i === null)
          throw new Error("Cannot swap the root fiber.");
        if (e.alternate = null, t.alternate = null, a.index = t.index, a.sibling = t.sibling, a.return = t.return, a.ref = t.ref, t === i.child)
          i.child = a;
        else {
          var u = i.child;
          if (u === null)
            throw new Error("Expected parent to have a child.");
          for (; u.sibling !== t; )
            if (u = u.sibling, u === null)
              throw new Error("Expected to find the previous sibling.");
          u.sibling = a;
        }
        var s = i.deletions;
        return s === null ? (i.deletions = [e], i.flags |= ka) : s.push(e), a.flags |= mn, a;
      }
    }
    function CS(e, t) {
      var a = e.lanes;
      return !!Jr(a, t);
    }
    function Mb(e, t, a) {
      switch (t.tag) {
        case J:
          v0(t), t.stateNode, bf();
          break;
        case ae:
          CC(t);
          break;
        case ce: {
          var i = t.type;
          Yl(i) && Ah(t);
          break;
        }
        case Se:
          hg(t, t.stateNode.containerInfo);
          break;
        case qe: {
          var u = t.memoizedProps.value, s = t.type._context;
          pC(t, s, u);
          break;
        }
        case it:
          {
            var f = Jr(a, t.childLanes);
            f && (t.flags |= Ct);
            {
              var p = t.stateNode;
              p.effectDuration = 0, p.passiveEffectDuration = 0;
            }
          }
          break;
        case ke: {
          var v = t.memoizedState;
          if (v !== null) {
            if (v.dehydrated !== null)
              return Ao(t, Lf(il.current)), t.flags |= _e, null;
            var y = t.child, g = y.childLanes;
            if (Jr(a, g))
              return m0(e, t, a);
            Ao(t, Lf(il.current));
            var b = Vu(e, t, a);
            return b !== null ? b.sibling : null;
          } else
            Ao(t, Lf(il.current));
          break;
        }
        case un: {
          var w = (e.flags & _e) !== De, N = Jr(a, t.childLanes);
          if (w) {
            if (N)
              return E0(e, t, a);
            t.flags |= _e;
          }
          var A = t.memoizedState;
          if (A !== null && (A.rendering = null, A.tail = null, A.lastEffect = null), Ao(t, il.current), N)
            break;
          return null;
        }
        case Me:
        case Ft:
          return t.lanes = $, f0(e, t, a);
      }
      return Vu(e, t, a);
    }
    function T0(e, t, a) {
      if (t._debugNeedsRemount && e !== null)
        return Lb(e, t, XS(t.type, t.key, t.pendingProps, t._debugOwner || null, t.mode, t.lanes));
      if (e !== null) {
        var i = e.memoizedProps, u = t.pendingProps;
        if (i !== u || zh() || // Force a re-render if the implementation changed due to hot reload:
        t.type !== e.type)
          ol = !0;
        else {
          var s = CS(e, a);
          if (!s && // If this is the second pass of an error or suspense boundary, there
          // may not be work scheduled on `current`, so we check for this flag.
          (t.flags & _e) === De)
            return ol = !1, Mb(e, t, a);
          (e.flags & wc) !== De ? ol = !0 : ol = !1;
        }
      } else if (ol = !1, Ar() && rx(t)) {
        var f = t.index, p = ax();
        XE(t, p, f);
      }
      switch (t.lanes = $, t.tag) {
        case tt:
          return pb(e, t, t.type, a);
        case ln: {
          var v = t.elementType;
          return fb(e, t, v, a);
        }
        case se: {
          var y = t.type, g = t.pendingProps, b = t.elementType === y ? g : ul(y, g);
          return pS(e, t, y, b, a);
        }
        case ce: {
          var w = t.type, N = t.pendingProps, A = t.elementType === w ? N : ul(w, N);
          return p0(e, t, w, A, a);
        }
        case J:
          return ob(e, t, a);
        case ae:
          return sb(e, t, a);
        case Ve:
          return cb(e, t);
        case ke:
          return m0(e, t, a);
        case Se:
          return kb(e, t, a);
        case Le: {
          var H = t.type, ue = t.pendingProps, ze = t.elementType === H ? ue : ul(H, ue);
          return o0(e, t, H, ze, a);
        }
        case at:
          return ib(e, t, a);
        case ct:
          return lb(e, t, a);
        case it:
          return ub(e, t, a);
        case qe:
          return Db(e, t, a);
        case gt:
          return Ob(e, t, a);
        case Qe: {
          var be = t.type, wt = t.pendingProps, yt = ul(be, wt);
          if (t.type !== t.elementType) {
            var O = be.propTypes;
            O && nl(
              O,
              yt,
              // Resolved for outer only
              "prop",
              xt(be)
            );
          }
          return yt = ul(be.type, yt), s0(e, t, be, yt, a);
        }
        case He:
          return c0(e, t, t.type, t.pendingProps, a);
        case Pt: {
          var P = t.type, L = t.pendingProps, q = t.elementType === P ? L : ul(P, L);
          return db(e, t, P, q, a);
        }
        case un:
          return E0(e, t, a);
        case _t:
          break;
        case Me:
          return f0(e, t, a);
      }
      throw new Error("Unknown unit of work tag (" + t.tag + "). This error is likely caused by a bug in React. Please file an issue.");
    }
    function jf(e) {
      e.flags |= Ct;
    }
    function w0(e) {
      e.flags |= En, e.flags |= ho;
    }
    var x0, RS, b0, _0;
    x0 = function(e, t, a, i) {
      for (var u = t.child; u !== null; ) {
        if (u.tag === ae || u.tag === Ve)
          ew(e, u.stateNode);
        else if (u.tag !== Se) {
          if (u.child !== null) {
            u.child.return = u, u = u.child;
            continue;
          }
        }
        if (u === t)
          return;
        for (; u.sibling === null; ) {
          if (u.return === null || u.return === t)
            return;
          u = u.return;
        }
        u.sibling.return = u.return, u = u.sibling;
      }
    }, RS = function(e, t) {
    }, b0 = function(e, t, a, i, u) {
      var s = e.memoizedProps;
      if (s !== i) {
        var f = t.stateNode, p = mg(), v = nw(f, a, s, i, u, p);
        t.updateQueue = v, v && jf(t);
      }
    }, _0 = function(e, t, a, i) {
      a !== i && jf(t);
    };
    function zp(e, t) {
      if (!Ar())
        switch (e.tailMode) {
          case "hidden": {
            for (var a = e.tail, i = null; a !== null; )
              a.alternate !== null && (i = a), a = a.sibling;
            i === null ? e.tail = null : i.sibling = null;
            break;
          }
          case "collapsed": {
            for (var u = e.tail, s = null; u !== null; )
              u.alternate !== null && (s = u), u = u.sibling;
            s === null ? !t && e.tail !== null ? e.tail.sibling = null : e.tail = null : s.sibling = null;
            break;
          }
        }
    }
    function Fr(e) {
      var t = e.alternate !== null && e.alternate.child === e.child, a = $, i = De;
      if (t) {
        if ((e.mode & Mt) !== Oe) {
          for (var v = e.selfBaseDuration, y = e.child; y !== null; )
            a = et(a, et(y.lanes, y.childLanes)), i |= y.subtreeFlags & zn, i |= y.flags & zn, v += y.treeBaseDuration, y = y.sibling;
          e.treeBaseDuration = v;
        } else
          for (var g = e.child; g !== null; )
            a = et(a, et(g.lanes, g.childLanes)), i |= g.subtreeFlags & zn, i |= g.flags & zn, g.return = e, g = g.sibling;
        e.subtreeFlags |= i;
      } else {
        if ((e.mode & Mt) !== Oe) {
          for (var u = e.actualDuration, s = e.selfBaseDuration, f = e.child; f !== null; )
            a = et(a, et(f.lanes, f.childLanes)), i |= f.subtreeFlags, i |= f.flags, u += f.actualDuration, s += f.treeBaseDuration, f = f.sibling;
          e.actualDuration = u, e.treeBaseDuration = s;
        } else
          for (var p = e.child; p !== null; )
            a = et(a, et(p.lanes, p.childLanes)), i |= p.subtreeFlags, i |= p.flags, p.return = e, p = p.sibling;
        e.subtreeFlags |= i;
      }
      return e.childLanes = a, t;
    }
    function Nb(e, t, a) {
      if (yx() && (t.mode & vt) !== Oe && (t.flags & _e) === De)
        return aC(t), bf(), t.flags |= Cr | os | Xn, !1;
      var i = Vh(t);
      if (a !== null && a.dehydrated !== null)
        if (e === null) {
          if (!i)
            throw new Error("A dehydrated suspense component was completed without a hydrated node. This is probably a bug in React.");
          if (hx(t), Fr(t), (t.mode & Mt) !== Oe) {
            var u = a !== null;
            if (u) {
              var s = t.child;
              s !== null && (t.treeBaseDuration -= s.treeBaseDuration);
            }
          }
          return !1;
        } else {
          if (bf(), (t.flags & _e) === De && (t.memoizedState = null), t.flags |= Ct, Fr(t), (t.mode & Mt) !== Oe) {
            var f = a !== null;
            if (f) {
              var p = t.child;
              p !== null && (t.treeBaseDuration -= p.treeBaseDuration);
            }
          }
          return !1;
        }
      else
        return iC(), !0;
    }
    function k0(e, t, a) {
      var i = t.pendingProps;
      switch (Gy(t), t.tag) {
        case tt:
        case ln:
        case He:
        case se:
        case Le:
        case at:
        case ct:
        case it:
        case gt:
        case Qe:
          return Fr(t), null;
        case ce: {
          var u = t.type;
          return Yl(u) && Uh(t), Fr(t), null;
        }
        case J: {
          var s = t.stateNode;
          if (Of(t), Yy(t), Cg(), s.pendingContext && (s.context = s.pendingContext, s.pendingContext = null), e === null || e.child === null) {
            var f = Vh(t);
            if (f)
              jf(t);
            else if (e !== null) {
              var p = e.memoizedState;
              // Check if this is a client root
              (!p.isDehydrated || // Check if we reverted to client rendering (e.g. due to an error)
              (t.flags & Cr) !== De) && (t.flags |= $n, iC());
            }
          }
          return RS(e, t), Fr(t), null;
        }
        case ae: {
          yg(t);
          var v = EC(), y = t.type;
          if (e !== null && t.stateNode != null)
            b0(e, t, y, i, v), e.ref !== t.ref && w0(t);
          else {
            if (!i) {
              if (t.stateNode === null)
                throw new Error("We must have new props for new mounts. This error is likely caused by a bug in React. Please file an issue.");
              return Fr(t), null;
            }
            var g = mg(), b = Vh(t);
            if (b)
              px(t, v, g) && jf(t);
            else {
              var w = JT(y, i, v, g, t);
              x0(w, t, !1, !1), t.stateNode = w, tw(w, y, i, v) && jf(t);
            }
            t.ref !== null && w0(t);
          }
          return Fr(t), null;
        }
        case Ve: {
          var N = i;
          if (e && t.stateNode != null) {
            var A = e.memoizedProps;
            _0(e, t, A, N);
          } else {
            if (typeof N != "string" && t.stateNode === null)
              throw new Error("We must have new props for new mounts. This error is likely caused by a bug in React. Please file an issue.");
            var H = EC(), ue = mg(), ze = Vh(t);
            ze ? vx(t) && jf(t) : t.stateNode = rw(N, H, ue, t);
          }
          return Fr(t), null;
        }
        case ke: {
          Mf(t);
          var be = t.memoizedState;
          if (e === null || e.memoizedState !== null && e.memoizedState.dehydrated !== null) {
            var wt = Nb(e, t, be);
            if (!wt)
              return t.flags & Xn ? t : null;
          }
          if ((t.flags & _e) !== De)
            return t.lanes = a, (t.mode & Mt) !== Oe && Qg(t), t;
          var yt = be !== null, O = e !== null && e.memoizedState !== null;
          if (yt !== O && yt) {
            var P = t.child;
            if (P.flags |= Nn, (t.mode & vt) !== Oe) {
              var L = e === null && (t.memoizedProps.unstable_avoidThisFallback !== !0 || !0);
              L || gg(il.current, TC) ? z1() : PS();
            }
          }
          var q = t.updateQueue;
          if (q !== null && (t.flags |= Ct), Fr(t), (t.mode & Mt) !== Oe && yt) {
            var pe = t.child;
            pe !== null && (t.treeBaseDuration -= pe.treeBaseDuration);
          }
          return null;
        }
        case Se:
          return Of(t), RS(e, t), e === null && qw(t.stateNode.containerInfo), Fr(t), null;
        case qe:
          var oe = t.type._context;
          return og(oe, t), Fr(t), null;
        case Pt: {
          var Ye = t.type;
          return Yl(Ye) && Uh(t), Fr(t), null;
        }
        case un: {
          Mf(t);
          var Xe = t.memoizedState;
          if (Xe === null)
            return Fr(t), null;
          var Xt = (t.flags & _e) !== De, Ut = Xe.rendering;
          if (Ut === null)
            if (Xt)
              zp(Xe, !1);
            else {
              var Gn = A1() && (e === null || (e.flags & _e) === De);
              if (!Gn)
                for (var At = t.child; At !== null; ) {
                  var Pn = rm(At);
                  if (Pn !== null) {
                    Xt = !0, t.flags |= _e, zp(Xe, !1);
                    var la = Pn.updateQueue;
                    return la !== null && (t.updateQueue = la, t.flags |= Ct), t.subtreeFlags = De, wx(t, a), Ao(t, Sg(il.current, Cp)), t.child;
                  }
                  At = At.sibling;
                }
              Xe.tail !== null && Qn() > K0() && (t.flags |= _e, Xt = !0, zp(Xe, !1), t.lanes = bd);
            }
          else {
            if (!Xt) {
              var Ir = rm(Ut);
              if (Ir !== null) {
                t.flags |= _e, Xt = !0;
                var si = Ir.updateQueue;
                if (si !== null && (t.updateQueue = si, t.flags |= Ct), zp(Xe, !0), Xe.tail === null && Xe.tailMode === "hidden" && !Ut.alternate && !Ar())
                  return Fr(t), null;
              } else // The time it took to render last row is greater than the remaining
              // time we have to render. So rendering one more row would likely
              // exceed it.
              Qn() * 2 - Xe.renderingStartTime > K0() && a !== Zr && (t.flags |= _e, Xt = !0, zp(Xe, !1), t.lanes = bd);
            }
            if (Xe.isBackwards)
              Ut.sibling = t.child, t.child = Ut;
            else {
              var Ca = Xe.last;
              Ca !== null ? Ca.sibling = Ut : t.child = Ut, Xe.last = Ut;
            }
          }
          if (Xe.tail !== null) {
            var Ra = Xe.tail;
            Xe.rendering = Ra, Xe.tail = Ra.sibling, Xe.renderingStartTime = Qn(), Ra.sibling = null;
            var ua = il.current;
            return Xt ? ua = Sg(ua, Cp) : ua = Lf(ua), Ao(t, ua), Ra;
          }
          return Fr(t), null;
        }
        case _t:
          break;
        case Me:
        case Ft: {
          HS(t);
          var Qu = t.memoizedState, $f = Qu !== null;
          if (e !== null) {
            var qp = e.memoizedState, Zl = qp !== null;
            Zl !== $f && // LegacyHidden doesn't do any hiding — it only pre-renders.
            !ne && (t.flags |= Nn);
          }
          return !$f || (t.mode & vt) === Oe ? Fr(t) : Jr(Xl, Zr) && (Fr(t), t.subtreeFlags & (mn | Ct) && (t.flags |= Nn)), null;
        }
        case kt:
          return null;
        case Ot:
          return null;
      }
      throw new Error("Unknown unit of work tag (" + t.tag + "). This error is likely caused by a bug in React. Please file an issue.");
    }
    function zb(e, t, a) {
      switch (Gy(t), t.tag) {
        case ce: {
          var i = t.type;
          Yl(i) && Uh(t);
          var u = t.flags;
          return u & Xn ? (t.flags = u & ~Xn | _e, (t.mode & Mt) !== Oe && Qg(t), t) : null;
        }
        case J: {
          t.stateNode, Of(t), Yy(t), Cg();
          var s = t.flags;
          return (s & Xn) !== De && (s & _e) === De ? (t.flags = s & ~Xn | _e, t) : null;
        }
        case ae:
          return yg(t), null;
        case ke: {
          Mf(t);
          var f = t.memoizedState;
          if (f !== null && f.dehydrated !== null) {
            if (t.alternate === null)
              throw new Error("Threw in newly mounted dehydrated component. This is likely a bug in React. Please file an issue.");
            bf();
          }
          var p = t.flags;
          return p & Xn ? (t.flags = p & ~Xn | _e, (t.mode & Mt) !== Oe && Qg(t), t) : null;
        }
        case un:
          return Mf(t), null;
        case Se:
          return Of(t), null;
        case qe:
          var v = t.type._context;
          return og(v, t), null;
        case Me:
        case Ft:
          return HS(t), null;
        case kt:
          return null;
        default:
          return null;
      }
    }
    function D0(e, t, a) {
      switch (Gy(t), t.tag) {
        case ce: {
          var i = t.type.childContextTypes;
          i != null && Uh(t);
          break;
        }
        case J: {
          t.stateNode, Of(t), Yy(t), Cg();
          break;
        }
        case ae: {
          yg(t);
          break;
        }
        case Se:
          Of(t);
          break;
        case ke:
          Mf(t);
          break;
        case un:
          Mf(t);
          break;
        case qe:
          var u = t.type._context;
          og(u, t);
          break;
        case Me:
        case Ft:
          HS(t);
          break;
      }
    }
    var O0 = null;
    O0 = /* @__PURE__ */ new Set();
    var _m = !1, Hr = !1, Ub = typeof WeakSet == "function" ? WeakSet : Set, ge = null, Ff = null, Hf = null;
    function Ab(e) {
      bl(null, function() {
        throw e;
      }), us();
    }
    var jb = function(e, t) {
      if (t.props = e.memoizedProps, t.state = e.memoizedState, e.mode & Mt)
        try {
          Kl(), t.componentWillUnmount();
        } finally {
          Gl(e);
        }
      else
        t.componentWillUnmount();
    };
    function L0(e, t) {
      try {
        Ho(fr, e);
      } catch (a) {
        fn(e, t, a);
      }
    }
    function TS(e, t, a) {
      try {
        jb(e, a);
      } catch (i) {
        fn(e, t, i);
      }
    }
    function Fb(e, t, a) {
      try {
        a.componentDidMount();
      } catch (i) {
        fn(e, t, i);
      }
    }
    function M0(e, t) {
      try {
        z0(e);
      } catch (a) {
        fn(e, t, a);
      }
    }
    function Pf(e, t) {
      var a = e.ref;
      if (a !== null)
        if (typeof a == "function") {
          var i;
          try {
            if (Pe && ft && e.mode & Mt)
              try {
                Kl(), i = a(null);
              } finally {
                Gl(e);
              }
            else
              i = a(null);
          } catch (u) {
            fn(e, t, u);
          }
          typeof i == "function" && S("Unexpected return value from a callback ref in %s. A callback ref should not return a function.", We(e));
        } else
          a.current = null;
    }
    function km(e, t, a) {
      try {
        a();
      } catch (i) {
        fn(e, t, i);
      }
    }
    var N0 = !1;
    function Hb(e, t) {
      XT(e.containerInfo), ge = t, Pb();
      var a = N0;
      return N0 = !1, a;
    }
    function Pb() {
      for (; ge !== null; ) {
        var e = ge, t = e.child;
        (e.subtreeFlags & kl) !== De && t !== null ? (t.return = e, ge = t) : Vb();
      }
    }
    function Vb() {
      for (; ge !== null; ) {
        var e = ge;
        Qt(e);
        try {
          Bb(e);
        } catch (a) {
          fn(e, e.return, a);
        }
        cn();
        var t = e.sibling;
        if (t !== null) {
          t.return = e.return, ge = t;
          return;
        }
        ge = e.return;
      }
    }
    function Bb(e) {
      var t = e.alternate, a = e.flags;
      if ((a & $n) !== De) {
        switch (Qt(e), e.tag) {
          case se:
          case Le:
          case He:
            break;
          case ce: {
            if (t !== null) {
              var i = t.memoizedProps, u = t.memoizedState, s = e.stateNode;
              e.type === e.elementType && !ec && (s.props !== e.memoizedProps && S("Expected %s props to match memoized props before getSnapshotBeforeUpdate. This might either be because of a bug in React, or because a component reassigns its own `this.props`. Please file an issue.", We(e) || "instance"), s.state !== e.memoizedState && S("Expected %s state to match memoized state before getSnapshotBeforeUpdate. This might either be because of a bug in React, or because a component reassigns its own `this.state`. Please file an issue.", We(e) || "instance"));
              var f = s.getSnapshotBeforeUpdate(e.elementType === e.type ? i : ul(e.type, i), u);
              {
                var p = O0;
                f === void 0 && !p.has(e.type) && (p.add(e.type), S("%s.getSnapshotBeforeUpdate(): A snapshot value (or null) must be returned. You have returned undefined.", We(e)));
              }
              s.__reactInternalSnapshotBeforeUpdate = f;
            }
            break;
          }
          case J: {
            {
              var v = e.stateNode;
              Rw(v.containerInfo);
            }
            break;
          }
          case ae:
          case Ve:
          case Se:
          case Pt:
            break;
          default:
            throw new Error("This unit of work tag should not have side-effects. This error is likely caused by a bug in React. Please file an issue.");
        }
        cn();
      }
    }
    function sl(e, t, a) {
      var i = t.updateQueue, u = i !== null ? i.lastEffect : null;
      if (u !== null) {
        var s = u.next, f = s;
        do {
          if ((f.tag & e) === e) {
            var p = f.destroy;
            f.destroy = void 0, p !== void 0 && ((e & jr) !== Ha ? qi(t) : (e & fr) !== Ha && cs(t), (e & $l) !== Ha && Wp(!0), km(t, a, p), (e & $l) !== Ha && Wp(!1), (e & jr) !== Ha ? Ml() : (e & fr) !== Ha && wd());
          }
          f = f.next;
        } while (f !== s);
      }
    }
    function Ho(e, t) {
      var a = t.updateQueue, i = a !== null ? a.lastEffect : null;
      if (i !== null) {
        var u = i.next, s = u;
        do {
          if ((s.tag & e) === e) {
            (e & jr) !== Ha ? Td(t) : (e & fr) !== Ha && Oc(t);
            var f = s.create;
            (e & $l) !== Ha && Wp(!0), s.destroy = f(), (e & $l) !== Ha && Wp(!1), (e & jr) !== Ha ? Nv() : (e & fr) !== Ha && zv();
            {
              var p = s.destroy;
              if (p !== void 0 && typeof p != "function") {
                var v = void 0;
                (s.tag & fr) !== De ? v = "useLayoutEffect" : (s.tag & $l) !== De ? v = "useInsertionEffect" : v = "useEffect";
                var y = void 0;
                p === null ? y = " You returned null. If your effect does not require clean up, return undefined (or nothing)." : typeof p.then == "function" ? y = `

It looks like you wrote ` + v + `(async () => ...) or returned a Promise. Instead, write the async function inside your effect and call it immediately:

` + v + `(() => {
  async function fetchData() {
    // You can await here
    const response = await MyAPI.getData(someId);
    // ...
  }
  fetchData();
}, [someId]); // Or [] if effect doesn't need props or state

Learn more about data fetching with Hooks: https://reactjs.org/link/hooks-data-fetching` : y = " You returned: " + p, S("%s must not return anything besides a function, which is used for clean-up.%s", v, y);
              }
            }
          }
          s = s.next;
        } while (s !== u);
      }
    }
    function Ib(e, t) {
      if ((t.flags & Ct) !== De)
        switch (t.tag) {
          case it: {
            var a = t.stateNode.passiveEffectDuration, i = t.memoizedProps, u = i.id, s = i.onPostCommit, f = KC(), p = t.alternate === null ? "mount" : "update";
            GC() && (p = "nested-update"), typeof s == "function" && s(u, p, a, f);
            var v = t.return;
            e: for (; v !== null; ) {
              switch (v.tag) {
                case J:
                  var y = v.stateNode;
                  y.passiveEffectDuration += a;
                  break e;
                case it:
                  var g = v.stateNode;
                  g.passiveEffectDuration += a;
                  break e;
              }
              v = v.return;
            }
            break;
          }
        }
    }
    function Yb(e, t, a, i) {
      if ((a.flags & Ol) !== De)
        switch (a.tag) {
          case se:
          case Le:
          case He: {
            if (!Hr)
              if (a.mode & Mt)
                try {
                  Kl(), Ho(fr | cr, a);
                } finally {
                  Gl(a);
                }
              else
                Ho(fr | cr, a);
            break;
          }
          case ce: {
            var u = a.stateNode;
            if (a.flags & Ct && !Hr)
              if (t === null)
                if (a.type === a.elementType && !ec && (u.props !== a.memoizedProps && S("Expected %s props to match memoized props before componentDidMount. This might either be because of a bug in React, or because a component reassigns its own `this.props`. Please file an issue.", We(a) || "instance"), u.state !== a.memoizedState && S("Expected %s state to match memoized state before componentDidMount. This might either be because of a bug in React, or because a component reassigns its own `this.state`. Please file an issue.", We(a) || "instance")), a.mode & Mt)
                  try {
                    Kl(), u.componentDidMount();
                  } finally {
                    Gl(a);
                  }
                else
                  u.componentDidMount();
              else {
                var s = a.elementType === a.type ? t.memoizedProps : ul(a.type, t.memoizedProps), f = t.memoizedState;
                if (a.type === a.elementType && !ec && (u.props !== a.memoizedProps && S("Expected %s props to match memoized props before componentDidUpdate. This might either be because of a bug in React, or because a component reassigns its own `this.props`. Please file an issue.", We(a) || "instance"), u.state !== a.memoizedState && S("Expected %s state to match memoized state before componentDidUpdate. This might either be because of a bug in React, or because a component reassigns its own `this.state`. Please file an issue.", We(a) || "instance")), a.mode & Mt)
                  try {
                    Kl(), u.componentDidUpdate(s, f, u.__reactInternalSnapshotBeforeUpdate);
                  } finally {
                    Gl(a);
                  }
                else
                  u.componentDidUpdate(s, f, u.__reactInternalSnapshotBeforeUpdate);
              }
            var p = a.updateQueue;
            p !== null && (a.type === a.elementType && !ec && (u.props !== a.memoizedProps && S("Expected %s props to match memoized props before processing the update queue. This might either be because of a bug in React, or because a component reassigns its own `this.props`. Please file an issue.", We(a) || "instance"), u.state !== a.memoizedState && S("Expected %s state to match memoized state before processing the update queue. This might either be because of a bug in React, or because a component reassigns its own `this.state`. Please file an issue.", We(a) || "instance")), SC(a, p, u));
            break;
          }
          case J: {
            var v = a.updateQueue;
            if (v !== null) {
              var y = null;
              if (a.child !== null)
                switch (a.child.tag) {
                  case ae:
                    y = a.child.stateNode;
                    break;
                  case ce:
                    y = a.child.stateNode;
                    break;
                }
              SC(a, v, y);
            }
            break;
          }
          case ae: {
            var g = a.stateNode;
            if (t === null && a.flags & Ct) {
              var b = a.type, w = a.memoizedProps;
              ow(g, b, w);
            }
            break;
          }
          case Ve:
            break;
          case Se:
            break;
          case it: {
            {
              var N = a.memoizedProps, A = N.onCommit, H = N.onRender, ue = a.stateNode.effectDuration, ze = KC(), be = t === null ? "mount" : "update";
              GC() && (be = "nested-update"), typeof H == "function" && H(a.memoizedProps.id, be, a.actualDuration, a.treeBaseDuration, a.actualStartTime, ze);
              {
                typeof A == "function" && A(a.memoizedProps.id, be, ue, ze), V1(a);
                var wt = a.return;
                e: for (; wt !== null; ) {
                  switch (wt.tag) {
                    case J:
                      var yt = wt.stateNode;
                      yt.effectDuration += ue;
                      break e;
                    case it:
                      var O = wt.stateNode;
                      O.effectDuration += ue;
                      break e;
                  }
                  wt = wt.return;
                }
              }
            }
            break;
          }
          case ke: {
            Zb(e, a);
            break;
          }
          case un:
          case Pt:
          case _t:
          case Me:
          case Ft:
          case Ot:
            break;
          default:
            throw new Error("This unit of work tag should not have side-effects. This error is likely caused by a bug in React. Please file an issue.");
        }
      Hr || a.flags & En && z0(a);
    }
    function $b(e) {
      switch (e.tag) {
        case se:
        case Le:
        case He: {
          if (e.mode & Mt)
            try {
              Kl(), L0(e, e.return);
            } finally {
              Gl(e);
            }
          else
            L0(e, e.return);
          break;
        }
        case ce: {
          var t = e.stateNode;
          typeof t.componentDidMount == "function" && Fb(e, e.return, t), M0(e, e.return);
          break;
        }
        case ae: {
          M0(e, e.return);
          break;
        }
      }
    }
    function Qb(e, t) {
      for (var a = null, i = e; ; ) {
        if (i.tag === ae) {
          if (a === null) {
            a = i;
            try {
              var u = i.stateNode;
              t ? gw(u) : Ew(i.stateNode, i.memoizedProps);
            } catch (f) {
              fn(e, e.return, f);
            }
          }
        } else if (i.tag === Ve) {
          if (a === null)
            try {
              var s = i.stateNode;
              t ? Sw(s) : Cw(s, i.memoizedProps);
            } catch (f) {
              fn(e, e.return, f);
            }
        } else if (!((i.tag === Me || i.tag === Ft) && i.memoizedState !== null && i !== e)) {
          if (i.child !== null) {
            i.child.return = i, i = i.child;
            continue;
          }
        }
        if (i === e)
          return;
        for (; i.sibling === null; ) {
          if (i.return === null || i.return === e)
            return;
          a === i && (a = null), i = i.return;
        }
        a === i && (a = null), i.sibling.return = i.return, i = i.sibling;
      }
    }
    function z0(e) {
      var t = e.ref;
      if (t !== null) {
        var a = e.stateNode, i;
        switch (e.tag) {
          case ae:
            i = a;
            break;
          default:
            i = a;
        }
        if (typeof t == "function") {
          var u;
          if (e.mode & Mt)
            try {
              Kl(), u = t(i);
            } finally {
              Gl(e);
            }
          else
            u = t(i);
          typeof u == "function" && S("Unexpected return value from a callback ref in %s. A callback ref should not return a function.", We(e));
        } else
          t.hasOwnProperty("current") || S("Unexpected ref object provided for %s. Use either a ref-setter function or React.createRef().", We(e)), t.current = i;
      }
    }
    function Wb(e) {
      var t = e.alternate;
      t !== null && (t.return = null), e.return = null;
    }
    function U0(e) {
      var t = e.alternate;
      t !== null && (e.alternate = null, U0(t));
      {
        if (e.child = null, e.deletions = null, e.sibling = null, e.tag === ae) {
          var a = e.stateNode;
          a !== null && Jw(a);
        }
        e.stateNode = null, e._debugOwner = null, e.return = null, e.dependencies = null, e.memoizedProps = null, e.memoizedState = null, e.pendingProps = null, e.stateNode = null, e.updateQueue = null;
      }
    }
    function Gb(e) {
      for (var t = e.return; t !== null; ) {
        if (A0(t))
          return t;
        t = t.return;
      }
      throw new Error("Expected to find a host parent. This error is likely caused by a bug in React. Please file an issue.");
    }
    function A0(e) {
      return e.tag === ae || e.tag === J || e.tag === Se;
    }
    function j0(e) {
      var t = e;
      e: for (; ; ) {
        for (; t.sibling === null; ) {
          if (t.return === null || A0(t.return))
            return null;
          t = t.return;
        }
        for (t.sibling.return = t.return, t = t.sibling; t.tag !== ae && t.tag !== Ve && t.tag !== Jt; ) {
          if (t.flags & mn || t.child === null || t.tag === Se)
            continue e;
          t.child.return = t, t = t.child;
        }
        if (!(t.flags & mn))
          return t.stateNode;
      }
    }
    function Kb(e) {
      var t = Gb(e);
      switch (t.tag) {
        case ae: {
          var a = t.stateNode;
          t.flags & Da && (HE(a), t.flags &= ~Da);
          var i = j0(e);
          xS(e, i, a);
          break;
        }
        case J:
        case Se: {
          var u = t.stateNode.containerInfo, s = j0(e);
          wS(e, s, u);
          break;
        }
        default:
          throw new Error("Invalid host parent fiber. This error is likely caused by a bug in React. Please file an issue.");
      }
    }
    function wS(e, t, a) {
      var i = e.tag, u = i === ae || i === Ve;
      if (u) {
        var s = e.stateNode;
        t ? vw(a, s, t) : dw(a, s);
      } else if (i !== Se) {
        var f = e.child;
        if (f !== null) {
          wS(f, t, a);
          for (var p = f.sibling; p !== null; )
            wS(p, t, a), p = p.sibling;
        }
      }
    }
    function xS(e, t, a) {
      var i = e.tag, u = i === ae || i === Ve;
      if (u) {
        var s = e.stateNode;
        t ? pw(a, s, t) : fw(a, s);
      } else if (i !== Se) {
        var f = e.child;
        if (f !== null) {
          xS(f, t, a);
          for (var p = f.sibling; p !== null; )
            xS(p, t, a), p = p.sibling;
        }
      }
    }
    var Pr = null, cl = !1;
    function qb(e, t, a) {
      {
        var i = t;
        e: for (; i !== null; ) {
          switch (i.tag) {
            case ae: {
              Pr = i.stateNode, cl = !1;
              break e;
            }
            case J: {
              Pr = i.stateNode.containerInfo, cl = !0;
              break e;
            }
            case Se: {
              Pr = i.stateNode.containerInfo, cl = !0;
              break e;
            }
          }
          i = i.return;
        }
        if (Pr === null)
          throw new Error("Expected to find a host parent. This error is likely caused by a bug in React. Please file an issue.");
        F0(e, t, a), Pr = null, cl = !1;
      }
      Wb(a);
    }
    function Po(e, t, a) {
      for (var i = a.child; i !== null; )
        F0(e, t, i), i = i.sibling;
    }
    function F0(e, t, a) {
      switch (Ed(a), a.tag) {
        case ae:
          Hr || Pf(a, t);
        case Ve: {
          {
            var i = Pr, u = cl;
            Pr = null, Po(e, t, a), Pr = i, cl = u, Pr !== null && (cl ? mw(Pr, a.stateNode) : hw(Pr, a.stateNode));
          }
          return;
        }
        case Jt: {
          Pr !== null && (cl ? yw(Pr, a.stateNode) : Ay(Pr, a.stateNode));
          return;
        }
        case Se: {
          {
            var s = Pr, f = cl;
            Pr = a.stateNode.containerInfo, cl = !0, Po(e, t, a), Pr = s, cl = f;
          }
          return;
        }
        case se:
        case Le:
        case Qe:
        case He: {
          if (!Hr) {
            var p = a.updateQueue;
            if (p !== null) {
              var v = p.lastEffect;
              if (v !== null) {
                var y = v.next, g = y;
                do {
                  var b = g, w = b.destroy, N = b.tag;
                  w !== void 0 && ((N & $l) !== Ha ? km(a, t, w) : (N & fr) !== Ha && (cs(a), a.mode & Mt ? (Kl(), km(a, t, w), Gl(a)) : km(a, t, w), wd())), g = g.next;
                } while (g !== y);
              }
            }
          }
          Po(e, t, a);
          return;
        }
        case ce: {
          if (!Hr) {
            Pf(a, t);
            var A = a.stateNode;
            typeof A.componentWillUnmount == "function" && TS(a, t, A);
          }
          Po(e, t, a);
          return;
        }
        case _t: {
          Po(e, t, a);
          return;
        }
        case Me: {
          if (
            // TODO: Remove this dead flag
            a.mode & vt
          ) {
            var H = Hr;
            Hr = H || a.memoizedState !== null, Po(e, t, a), Hr = H;
          } else
            Po(e, t, a);
          break;
        }
        default: {
          Po(e, t, a);
          return;
        }
      }
    }
    function Xb(e) {
      e.memoizedState;
    }
    function Zb(e, t) {
      var a = t.memoizedState;
      if (a === null) {
        var i = t.alternate;
        if (i !== null) {
          var u = i.memoizedState;
          if (u !== null) {
            var s = u.dehydrated;
            s !== null && Aw(s);
          }
        }
      }
    }
    function H0(e) {
      var t = e.updateQueue;
      if (t !== null) {
        e.updateQueue = null;
        var a = e.stateNode;
        a === null && (a = e.stateNode = new Ub()), t.forEach(function(i) {
          var u = G1.bind(null, e, i);
          if (!a.has(i)) {
            if (a.add(i), Xr)
              if (Ff !== null && Hf !== null)
                Qp(Hf, Ff);
              else
                throw Error("Expected finished root and lanes to be set. This is a bug in React.");
            i.then(u, u);
          }
        });
      }
    }
    function Jb(e, t, a) {
      Ff = a, Hf = e, Qt(t), P0(t, e), Qt(t), Ff = null, Hf = null;
    }
    function fl(e, t, a) {
      var i = t.deletions;
      if (i !== null)
        for (var u = 0; u < i.length; u++) {
          var s = i[u];
          try {
            qb(e, t, s);
          } catch (v) {
            fn(s, t, v);
          }
        }
      var f = Sl();
      if (t.subtreeFlags & Dl)
        for (var p = t.child; p !== null; )
          Qt(p), P0(p, e), p = p.sibling;
      Qt(f);
    }
    function P0(e, t, a) {
      var i = e.alternate, u = e.flags;
      switch (e.tag) {
        case se:
        case Le:
        case Qe:
        case He: {
          if (fl(t, e), ql(e), u & Ct) {
            try {
              sl($l | cr, e, e.return), Ho($l | cr, e);
            } catch (Ye) {
              fn(e, e.return, Ye);
            }
            if (e.mode & Mt) {
              try {
                Kl(), sl(fr | cr, e, e.return);
              } catch (Ye) {
                fn(e, e.return, Ye);
              }
              Gl(e);
            } else
              try {
                sl(fr | cr, e, e.return);
              } catch (Ye) {
                fn(e, e.return, Ye);
              }
          }
          return;
        }
        case ce: {
          fl(t, e), ql(e), u & En && i !== null && Pf(i, i.return);
          return;
        }
        case ae: {
          fl(t, e), ql(e), u & En && i !== null && Pf(i, i.return);
          {
            if (e.flags & Da) {
              var s = e.stateNode;
              try {
                HE(s);
              } catch (Ye) {
                fn(e, e.return, Ye);
              }
            }
            if (u & Ct) {
              var f = e.stateNode;
              if (f != null) {
                var p = e.memoizedProps, v = i !== null ? i.memoizedProps : p, y = e.type, g = e.updateQueue;
                if (e.updateQueue = null, g !== null)
                  try {
                    sw(f, g, y, v, p, e);
                  } catch (Ye) {
                    fn(e, e.return, Ye);
                  }
              }
            }
          }
          return;
        }
        case Ve: {
          if (fl(t, e), ql(e), u & Ct) {
            if (e.stateNode === null)
              throw new Error("This should have a text node initialized. This error is likely caused by a bug in React. Please file an issue.");
            var b = e.stateNode, w = e.memoizedProps, N = i !== null ? i.memoizedProps : w;
            try {
              cw(b, N, w);
            } catch (Ye) {
              fn(e, e.return, Ye);
            }
          }
          return;
        }
        case J: {
          if (fl(t, e), ql(e), u & Ct && i !== null) {
            var A = i.memoizedState;
            if (A.isDehydrated)
              try {
                Uw(t.containerInfo);
              } catch (Ye) {
                fn(e, e.return, Ye);
              }
          }
          return;
        }
        case Se: {
          fl(t, e), ql(e);
          return;
        }
        case ke: {
          fl(t, e), ql(e);
          var H = e.child;
          if (H.flags & Nn) {
            var ue = H.stateNode, ze = H.memoizedState, be = ze !== null;
            if (ue.isHidden = be, be) {
              var wt = H.alternate !== null && H.alternate.memoizedState !== null;
              wt || N1();
            }
          }
          if (u & Ct) {
            try {
              Xb(e);
            } catch (Ye) {
              fn(e, e.return, Ye);
            }
            H0(e);
          }
          return;
        }
        case Me: {
          var yt = i !== null && i.memoizedState !== null;
          if (
            // TODO: Remove this dead flag
            e.mode & vt
          ) {
            var O = Hr;
            Hr = O || yt, fl(t, e), Hr = O;
          } else
            fl(t, e);
          if (ql(e), u & Nn) {
            var P = e.stateNode, L = e.memoizedState, q = L !== null, pe = e;
            if (P.isHidden = q, q && !yt && (pe.mode & vt) !== Oe) {
              ge = pe;
              for (var oe = pe.child; oe !== null; )
                ge = oe, t1(oe), oe = oe.sibling;
            }
            Qb(pe, q);
          }
          return;
        }
        case un: {
          fl(t, e), ql(e), u & Ct && H0(e);
          return;
        }
        case _t:
          return;
        default: {
          fl(t, e), ql(e);
          return;
        }
      }
    }
    function ql(e) {
      var t = e.flags;
      if (t & mn) {
        try {
          Kb(e);
        } catch (a) {
          fn(e, e.return, a);
        }
        e.flags &= ~mn;
      }
      t & Gr && (e.flags &= ~Gr);
    }
    function e1(e, t, a) {
      Ff = a, Hf = t, ge = e, V0(e, t, a), Ff = null, Hf = null;
    }
    function V0(e, t, a) {
      for (var i = (e.mode & vt) !== Oe; ge !== null; ) {
        var u = ge, s = u.child;
        if (u.tag === Me && i) {
          var f = u.memoizedState !== null, p = f || _m;
          if (p) {
            bS(e, t, a);
            continue;
          } else {
            var v = u.alternate, y = v !== null && v.memoizedState !== null, g = y || Hr, b = _m, w = Hr;
            _m = p, Hr = g, Hr && !w && (ge = u, n1(u));
            for (var N = s; N !== null; )
              ge = N, V0(
                N,
                // New root; bubble back up to here and stop.
                t,
                a
              ), N = N.sibling;
            ge = u, _m = b, Hr = w, bS(e, t, a);
            continue;
          }
        }
        (u.subtreeFlags & Ol) !== De && s !== null ? (s.return = u, ge = s) : bS(e, t, a);
      }
    }
    function bS(e, t, a) {
      for (; ge !== null; ) {
        var i = ge;
        if ((i.flags & Ol) !== De) {
          var u = i.alternate;
          Qt(i);
          try {
            Yb(t, u, i, a);
          } catch (f) {
            fn(i, i.return, f);
          }
          cn();
        }
        if (i === e) {
          ge = null;
          return;
        }
        var s = i.sibling;
        if (s !== null) {
          s.return = i.return, ge = s;
          return;
        }
        ge = i.return;
      }
    }
    function t1(e) {
      for (; ge !== null; ) {
        var t = ge, a = t.child;
        switch (t.tag) {
          case se:
          case Le:
          case Qe:
          case He: {
            if (t.mode & Mt)
              try {
                Kl(), sl(fr, t, t.return);
              } finally {
                Gl(t);
              }
            else
              sl(fr, t, t.return);
            break;
          }
          case ce: {
            Pf(t, t.return);
            var i = t.stateNode;
            typeof i.componentWillUnmount == "function" && TS(t, t.return, i);
            break;
          }
          case ae: {
            Pf(t, t.return);
            break;
          }
          case Me: {
            var u = t.memoizedState !== null;
            if (u) {
              B0(e);
              continue;
            }
            break;
          }
        }
        a !== null ? (a.return = t, ge = a) : B0(e);
      }
    }
    function B0(e) {
      for (; ge !== null; ) {
        var t = ge;
        if (t === e) {
          ge = null;
          return;
        }
        var a = t.sibling;
        if (a !== null) {
          a.return = t.return, ge = a;
          return;
        }
        ge = t.return;
      }
    }
    function n1(e) {
      for (; ge !== null; ) {
        var t = ge, a = t.child;
        if (t.tag === Me) {
          var i = t.memoizedState !== null;
          if (i) {
            I0(e);
            continue;
          }
        }
        a !== null ? (a.return = t, ge = a) : I0(e);
      }
    }
    function I0(e) {
      for (; ge !== null; ) {
        var t = ge;
        Qt(t);
        try {
          $b(t);
        } catch (i) {
          fn(t, t.return, i);
        }
        if (cn(), t === e) {
          ge = null;
          return;
        }
        var a = t.sibling;
        if (a !== null) {
          a.return = t.return, ge = a;
          return;
        }
        ge = t.return;
      }
    }
    function r1(e, t, a, i) {
      ge = t, a1(t, e, a, i);
    }
    function a1(e, t, a, i) {
      for (; ge !== null; ) {
        var u = ge, s = u.child;
        (u.subtreeFlags & Gi) !== De && s !== null ? (s.return = u, ge = s) : i1(e, t, a, i);
      }
    }
    function i1(e, t, a, i) {
      for (; ge !== null; ) {
        var u = ge;
        if ((u.flags & Wr) !== De) {
          Qt(u);
          try {
            l1(t, u, a, i);
          } catch (f) {
            fn(u, u.return, f);
          }
          cn();
        }
        if (u === e) {
          ge = null;
          return;
        }
        var s = u.sibling;
        if (s !== null) {
          s.return = u.return, ge = s;
          return;
        }
        ge = u.return;
      }
    }
    function l1(e, t, a, i) {
      switch (t.tag) {
        case se:
        case Le:
        case He: {
          if (t.mode & Mt) {
            $g();
            try {
              Ho(jr | cr, t);
            } finally {
              Yg(t);
            }
          } else
            Ho(jr | cr, t);
          break;
        }
      }
    }
    function u1(e) {
      ge = e, o1();
    }
    function o1() {
      for (; ge !== null; ) {
        var e = ge, t = e.child;
        if ((ge.flags & ka) !== De) {
          var a = e.deletions;
          if (a !== null) {
            for (var i = 0; i < a.length; i++) {
              var u = a[i];
              ge = u, f1(u, e);
            }
            {
              var s = e.alternate;
              if (s !== null) {
                var f = s.child;
                if (f !== null) {
                  s.child = null;
                  do {
                    var p = f.sibling;
                    f.sibling = null, f = p;
                  } while (f !== null);
                }
              }
            }
            ge = e;
          }
        }
        (e.subtreeFlags & Gi) !== De && t !== null ? (t.return = e, ge = t) : s1();
      }
    }
    function s1() {
      for (; ge !== null; ) {
        var e = ge;
        (e.flags & Wr) !== De && (Qt(e), c1(e), cn());
        var t = e.sibling;
        if (t !== null) {
          t.return = e.return, ge = t;
          return;
        }
        ge = e.return;
      }
    }
    function c1(e) {
      switch (e.tag) {
        case se:
        case Le:
        case He: {
          e.mode & Mt ? ($g(), sl(jr | cr, e, e.return), Yg(e)) : sl(jr | cr, e, e.return);
          break;
        }
      }
    }
    function f1(e, t) {
      for (; ge !== null; ) {
        var a = ge;
        Qt(a), p1(a, t), cn();
        var i = a.child;
        i !== null ? (i.return = a, ge = i) : d1(e);
      }
    }
    function d1(e) {
      for (; ge !== null; ) {
        var t = ge, a = t.sibling, i = t.return;
        if (U0(t), t === e) {
          ge = null;
          return;
        }
        if (a !== null) {
          a.return = i, ge = a;
          return;
        }
        ge = i;
      }
    }
    function p1(e, t) {
      switch (e.tag) {
        case se:
        case Le:
        case He: {
          e.mode & Mt ? ($g(), sl(jr, e, t), Yg(e)) : sl(jr, e, t);
          break;
        }
      }
    }
    function v1(e) {
      switch (e.tag) {
        case se:
        case Le:
        case He: {
          try {
            Ho(fr | cr, e);
          } catch (a) {
            fn(e, e.return, a);
          }
          break;
        }
        case ce: {
          var t = e.stateNode;
          try {
            t.componentDidMount();
          } catch (a) {
            fn(e, e.return, a);
          }
          break;
        }
      }
    }
    function h1(e) {
      switch (e.tag) {
        case se:
        case Le:
        case He: {
          try {
            Ho(jr | cr, e);
          } catch (t) {
            fn(e, e.return, t);
          }
          break;
        }
      }
    }
    function m1(e) {
      switch (e.tag) {
        case se:
        case Le:
        case He: {
          try {
            sl(fr | cr, e, e.return);
          } catch (a) {
            fn(e, e.return, a);
          }
          break;
        }
        case ce: {
          var t = e.stateNode;
          typeof t.componentWillUnmount == "function" && TS(e, e.return, t);
          break;
        }
      }
    }
    function y1(e) {
      switch (e.tag) {
        case se:
        case Le:
        case He:
          try {
            sl(jr | cr, e, e.return);
          } catch (t) {
            fn(e, e.return, t);
          }
      }
    }
    if (typeof Symbol == "function" && Symbol.for) {
      var Up = Symbol.for;
      Up("selector.component"), Up("selector.has_pseudo_class"), Up("selector.role"), Up("selector.test_id"), Up("selector.text");
    }
    var g1 = [];
    function S1() {
      g1.forEach(function(e) {
        return e();
      });
    }
    var E1 = k.ReactCurrentActQueue;
    function C1(e) {
      {
        var t = (
          // $FlowExpectedError – Flow doesn't know about IS_REACT_ACT_ENVIRONMENT global
          typeof IS_REACT_ACT_ENVIRONMENT < "u" ? IS_REACT_ACT_ENVIRONMENT : void 0
        ), a = typeof jest < "u";
        return a && t !== !1;
      }
    }
    function Y0() {
      {
        var e = (
          // $FlowExpectedError – Flow doesn't know about IS_REACT_ACT_ENVIRONMENT global
          typeof IS_REACT_ACT_ENVIRONMENT < "u" ? IS_REACT_ACT_ENVIRONMENT : void 0
        );
        return !e && E1.current !== null && S("The current testing environment is not configured to support act(...)"), e;
      }
    }
    var R1 = Math.ceil, _S = k.ReactCurrentDispatcher, kS = k.ReactCurrentOwner, Vr = k.ReactCurrentBatchConfig, dl = k.ReactCurrentActQueue, vr = (
      /*             */
      0
    ), $0 = (
      /*               */
      1
    ), Br = (
      /*                */
      2
    ), ji = (
      /*                */
      4
    ), Bu = 0, Ap = 1, tc = 2, Dm = 3, jp = 4, Q0 = 5, DS = 6, Tt = vr, Sa = null, Dn = null, hr = $, Xl = $, OS = Oo($), mr = Bu, Fp = null, Om = $, Hp = $, Lm = $, Pp = null, Pa = null, LS = 0, W0 = 500, G0 = 1 / 0, T1 = 500, Iu = null;
    function Vp() {
      G0 = Qn() + T1;
    }
    function K0() {
      return G0;
    }
    var Mm = !1, MS = null, Vf = null, nc = !1, Vo = null, Bp = $, NS = [], zS = null, w1 = 50, Ip = 0, US = null, AS = !1, Nm = !1, x1 = 50, Bf = 0, zm = null, Yp = Zt, Um = $, q0 = !1;
    function Am() {
      return Sa;
    }
    function Ea() {
      return (Tt & (Br | ji)) !== vr ? Qn() : (Yp !== Zt || (Yp = Qn()), Yp);
    }
    function Bo(e) {
      var t = e.mode;
      if ((t & vt) === Oe)
        return Be;
      if ((Tt & Br) !== vr && hr !== $)
        return Ts(hr);
      var a = Ex() !== Sx;
      if (a) {
        if (Vr.transition !== null) {
          var i = Vr.transition;
          i._updatedFibers || (i._updatedFibers = /* @__PURE__ */ new Set()), i._updatedFibers.add(e);
        }
        return Um === Dt && (Um = Md()), Um;
      }
      var u = Ua();
      if (u !== Dt)
        return u;
      var s = aw();
      return s;
    }
    function b1(e) {
      var t = e.mode;
      return (t & vt) === Oe ? Be : Pv();
    }
    function yr(e, t, a, i) {
      q1(), q0 && S("useInsertionEffect must not schedule updates."), AS && (Nm = !0), So(e, a, i), (Tt & Br) !== $ && e === Sa ? J1(t) : (Xr && bs(e, t, a), e_(t), e === Sa && ((Tt & Br) === vr && (Hp = et(Hp, a)), mr === jp && Io(e, hr)), Va(e, i), a === Be && Tt === vr && (t.mode & vt) === Oe && // Treat `act` as if it's inside `batchedUpdates`, even in legacy mode.
      !dl.isBatchingLegacy && (Vp(), qE()));
    }
    function _1(e, t, a) {
      var i = e.current;
      i.lanes = t, So(e, t, a), Va(e, a);
    }
    function k1(e) {
      return (
        // TODO: Remove outdated deferRenderPhaseUpdateToNextBatch experiment. We
        // decided not to enable it.
        (Tt & Br) !== vr
      );
    }
    function Va(e, t) {
      var a = e.callbackNode;
      qc(e, t);
      var i = Kc(e, e === Sa ? hr : $);
      if (i === $) {
        a !== null && dR(a), e.callbackNode = null, e.callbackPriority = Dt;
        return;
      }
      var u = Ul(i), s = e.callbackPriority;
      if (s === u && // Special case related to `act`. If the currently scheduled task is a
      // Scheduler task, rather than an `act` task, cancel it and re-scheduled
      // on the `act` queue.
      !(dl.current !== null && a !== IS)) {
        a == null && s !== Be && S("Expected scheduled callback to exist. This error is likely caused by a bug in React. Please file an issue.");
        return;
      }
      a != null && dR(a);
      var f;
      if (u === Be)
        e.tag === Lo ? (dl.isBatchingLegacy !== null && (dl.didScheduleLegacyUpdate = !0), nx(J0.bind(null, e))) : KE(J0.bind(null, e)), dl.current !== null ? dl.current.push(Mo) : lw(function() {
          (Tt & (Br | ji)) === vr && Mo();
        }), f = null;
      else {
        var p;
        switch (Wv(i)) {
          case Lr:
            p = ss;
            break;
          case _i:
            p = Ll;
            break;
          case Na:
            p = Ki;
            break;
          case za:
            p = mu;
            break;
          default:
            p = Ki;
            break;
        }
        f = YS(p, X0.bind(null, e));
      }
      e.callbackPriority = u, e.callbackNode = f;
    }
    function X0(e, t) {
      if (Qx(), Yp = Zt, Um = $, (Tt & (Br | ji)) !== vr)
        throw new Error("Should not already be working.");
      var a = e.callbackNode, i = $u();
      if (i && e.callbackNode !== a)
        return null;
      var u = Kc(e, e === Sa ? hr : $);
      if (u === $)
        return null;
      var s = !Zc(e, u) && !Hv(e, u) && !t, f = s ? F1(e, u) : Fm(e, u);
      if (f !== Bu) {
        if (f === tc) {
          var p = Xc(e);
          p !== $ && (u = p, f = jS(e, p));
        }
        if (f === Ap) {
          var v = Fp;
          throw rc(e, $), Io(e, u), Va(e, Qn()), v;
        }
        if (f === DS)
          Io(e, u);
        else {
          var y = !Zc(e, u), g = e.current.alternate;
          if (y && !O1(g)) {
            if (f = Fm(e, u), f === tc) {
              var b = Xc(e);
              b !== $ && (u = b, f = jS(e, b));
            }
            if (f === Ap) {
              var w = Fp;
              throw rc(e, $), Io(e, u), Va(e, Qn()), w;
            }
          }
          e.finishedWork = g, e.finishedLanes = u, D1(e, f, u);
        }
      }
      return Va(e, Qn()), e.callbackNode === a ? X0.bind(null, e) : null;
    }
    function jS(e, t) {
      var a = Pp;
      if (tf(e)) {
        var i = rc(e, t);
        i.flags |= Cr, Kw(e.containerInfo);
      }
      var u = Fm(e, t);
      if (u !== tc) {
        var s = Pa;
        Pa = a, s !== null && Z0(s);
      }
      return u;
    }
    function Z0(e) {
      Pa === null ? Pa = e : Pa.push.apply(Pa, e);
    }
    function D1(e, t, a) {
      switch (t) {
        case Bu:
        case Ap:
          throw new Error("Root did not complete. This is a bug in React.");
        case tc: {
          ac(e, Pa, Iu);
          break;
        }
        case Dm: {
          if (Io(e, a), _u(a) && // do not delay if we're inside an act() scope
          !pR()) {
            var i = LS + W0 - Qn();
            if (i > 10) {
              var u = Kc(e, $);
              if (u !== $)
                break;
              var s = e.suspendedLanes;
              if (!ku(s, a)) {
                Ea(), Jc(e, s);
                break;
              }
              e.timeoutHandle = zy(ac.bind(null, e, Pa, Iu), i);
              break;
            }
          }
          ac(e, Pa, Iu);
          break;
        }
        case jp: {
          if (Io(e, a), Od(a))
            break;
          if (!pR()) {
            var f = ai(e, a), p = f, v = Qn() - p, y = K1(v) - v;
            if (y > 10) {
              e.timeoutHandle = zy(ac.bind(null, e, Pa, Iu), y);
              break;
            }
          }
          ac(e, Pa, Iu);
          break;
        }
        case Q0: {
          ac(e, Pa, Iu);
          break;
        }
        default:
          throw new Error("Unknown root exit status.");
      }
    }
    function O1(e) {
      for (var t = e; ; ) {
        if (t.flags & vo) {
          var a = t.updateQueue;
          if (a !== null) {
            var i = a.stores;
            if (i !== null)
              for (var u = 0; u < i.length; u++) {
                var s = i[u], f = s.getSnapshot, p = s.value;
                try {
                  if (!G(f(), p))
                    return !1;
                } catch {
                  return !1;
                }
              }
          }
        }
        var v = t.child;
        if (t.subtreeFlags & vo && v !== null) {
          v.return = t, t = v;
          continue;
        }
        if (t === e)
          return !0;
        for (; t.sibling === null; ) {
          if (t.return === null || t.return === e)
            return !0;
          t = t.return;
        }
        t.sibling.return = t.return, t = t.sibling;
      }
      return !0;
    }
    function Io(e, t) {
      t = ws(t, Lm), t = ws(t, Hp), Iv(e, t);
    }
    function J0(e) {
      if (Wx(), (Tt & (Br | ji)) !== vr)
        throw new Error("Should not already be working.");
      $u();
      var t = Kc(e, $);
      if (!Jr(t, Be))
        return Va(e, Qn()), null;
      var a = Fm(e, t);
      if (e.tag !== Lo && a === tc) {
        var i = Xc(e);
        i !== $ && (t = i, a = jS(e, i));
      }
      if (a === Ap) {
        var u = Fp;
        throw rc(e, $), Io(e, t), Va(e, Qn()), u;
      }
      if (a === DS)
        throw new Error("Root did not complete. This is a bug in React.");
      var s = e.current.alternate;
      return e.finishedWork = s, e.finishedLanes = t, ac(e, Pa, Iu), Va(e, Qn()), null;
    }
    function L1(e, t) {
      t !== $ && (ef(e, et(t, Be)), Va(e, Qn()), (Tt & (Br | ji)) === vr && (Vp(), Mo()));
    }
    function FS(e, t) {
      var a = Tt;
      Tt |= $0;
      try {
        return e(t);
      } finally {
        Tt = a, Tt === vr && // Treat `act` as if it's inside `batchedUpdates`, even in legacy mode.
        !dl.isBatchingLegacy && (Vp(), qE());
      }
    }
    function M1(e, t, a, i, u) {
      var s = Ua(), f = Vr.transition;
      try {
        return Vr.transition = null, jn(Lr), e(t, a, i, u);
      } finally {
        jn(s), Vr.transition = f, Tt === vr && Vp();
      }
    }
    function Yu(e) {
      Vo !== null && Vo.tag === Lo && (Tt & (Br | ji)) === vr && $u();
      var t = Tt;
      Tt |= $0;
      var a = Vr.transition, i = Ua();
      try {
        return Vr.transition = null, jn(Lr), e ? e() : void 0;
      } finally {
        jn(i), Vr.transition = a, Tt = t, (Tt & (Br | ji)) === vr && Mo();
      }
    }
    function eR() {
      return (Tt & (Br | ji)) !== vr;
    }
    function jm(e, t) {
      aa(OS, Xl, e), Xl = et(Xl, t);
    }
    function HS(e) {
      Xl = OS.current, ra(OS, e);
    }
    function rc(e, t) {
      e.finishedWork = null, e.finishedLanes = $;
      var a = e.timeoutHandle;
      if (a !== Uy && (e.timeoutHandle = Uy, iw(a)), Dn !== null)
        for (var i = Dn.return; i !== null; ) {
          var u = i.alternate;
          D0(u, i), i = i.return;
        }
      Sa = e;
      var s = ic(e.current, null);
      return Dn = s, hr = Xl = t, mr = Bu, Fp = null, Om = $, Hp = $, Lm = $, Pp = null, Pa = null, _x(), al.discardPendingWarnings(), s;
    }
    function tR(e, t) {
      do {
        var a = Dn;
        try {
          if (Wh(), xC(), cn(), kS.current = null, a === null || a.return === null) {
            mr = Ap, Fp = t, Dn = null;
            return;
          }
          if (Pe && a.mode & Mt && Rm(a, !0), Ie)
            if (ha(), t !== null && typeof t == "object" && typeof t.then == "function") {
              var i = t;
              bi(a, i, hr);
            } else
              fs(a, t, hr);
          nb(e, a.return, a, t, hr), iR(a);
        } catch (u) {
          t = u, Dn === a && a !== null ? (a = a.return, Dn = a) : a = Dn;
          continue;
        }
        return;
      } while (!0);
    }
    function nR() {
      var e = _S.current;
      return _S.current = ym, e === null ? ym : e;
    }
    function rR(e) {
      _S.current = e;
    }
    function N1() {
      LS = Qn();
    }
    function $p(e) {
      Om = et(e, Om);
    }
    function z1() {
      mr === Bu && (mr = Dm);
    }
    function PS() {
      (mr === Bu || mr === Dm || mr === tc) && (mr = jp), Sa !== null && (Rs(Om) || Rs(Hp)) && Io(Sa, hr);
    }
    function U1(e) {
      mr !== jp && (mr = tc), Pp === null ? Pp = [e] : Pp.push(e);
    }
    function A1() {
      return mr === Bu;
    }
    function Fm(e, t) {
      var a = Tt;
      Tt |= Br;
      var i = nR();
      if (Sa !== e || hr !== t) {
        if (Xr) {
          var u = e.memoizedUpdaters;
          u.size > 0 && (Qp(e, hr), u.clear()), Yv(e, t);
        }
        Iu = Ad(), rc(e, t);
      }
      Eu(t);
      do
        try {
          j1();
          break;
        } catch (s) {
          tR(e, s);
        }
      while (!0);
      if (Wh(), Tt = a, rR(i), Dn !== null)
        throw new Error("Cannot commit an incomplete root. This error is likely caused by a bug in React. Please file an issue.");
      return Lc(), Sa = null, hr = $, mr;
    }
    function j1() {
      for (; Dn !== null; )
        aR(Dn);
    }
    function F1(e, t) {
      var a = Tt;
      Tt |= Br;
      var i = nR();
      if (Sa !== e || hr !== t) {
        if (Xr) {
          var u = e.memoizedUpdaters;
          u.size > 0 && (Qp(e, hr), u.clear()), Yv(e, t);
        }
        Iu = Ad(), Vp(), rc(e, t);
      }
      Eu(t);
      do
        try {
          H1();
          break;
        } catch (s) {
          tR(e, s);
        }
      while (!0);
      return Wh(), rR(i), Tt = a, Dn !== null ? (Uv(), Bu) : (Lc(), Sa = null, hr = $, mr);
    }
    function H1() {
      for (; Dn !== null && !hd(); )
        aR(Dn);
    }
    function aR(e) {
      var t = e.alternate;
      Qt(e);
      var a;
      (e.mode & Mt) !== Oe ? (Ig(e), a = VS(t, e, Xl), Rm(e, !0)) : a = VS(t, e, Xl), cn(), e.memoizedProps = e.pendingProps, a === null ? iR(e) : Dn = a, kS.current = null;
    }
    function iR(e) {
      var t = e;
      do {
        var a = t.alternate, i = t.return;
        if ((t.flags & os) === De) {
          Qt(t);
          var u = void 0;
          if ((t.mode & Mt) === Oe ? u = k0(a, t, Xl) : (Ig(t), u = k0(a, t, Xl), Rm(t, !1)), cn(), u !== null) {
            Dn = u;
            return;
          }
        } else {
          var s = zb(a, t);
          if (s !== null) {
            s.flags &= Dv, Dn = s;
            return;
          }
          if ((t.mode & Mt) !== Oe) {
            Rm(t, !1);
            for (var f = t.actualDuration, p = t.child; p !== null; )
              f += p.actualDuration, p = p.sibling;
            t.actualDuration = f;
          }
          if (i !== null)
            i.flags |= os, i.subtreeFlags = De, i.deletions = null;
          else {
            mr = DS, Dn = null;
            return;
          }
        }
        var v = t.sibling;
        if (v !== null) {
          Dn = v;
          return;
        }
        t = i, Dn = t;
      } while (t !== null);
      mr === Bu && (mr = Q0);
    }
    function ac(e, t, a) {
      var i = Ua(), u = Vr.transition;
      try {
        Vr.transition = null, jn(Lr), P1(e, t, a, i);
      } finally {
        Vr.transition = u, jn(i);
      }
      return null;
    }
    function P1(e, t, a, i) {
      do
        $u();
      while (Vo !== null);
      if (X1(), (Tt & (Br | ji)) !== vr)
        throw new Error("Should not already be working.");
      var u = e.finishedWork, s = e.finishedLanes;
      if (Cd(s), u === null)
        return Rd(), null;
      if (s === $ && S("root.finishedLanes should not be empty during a commit. This is a bug in React."), e.finishedWork = null, e.finishedLanes = $, u === e.current)
        throw new Error("Cannot commit the same tree as before. This error is likely caused by a bug in React. Please file an issue.");
      e.callbackNode = null, e.callbackPriority = Dt;
      var f = et(u.lanes, u.childLanes);
      zd(e, f), e === Sa && (Sa = null, Dn = null, hr = $), ((u.subtreeFlags & Gi) !== De || (u.flags & Gi) !== De) && (nc || (nc = !0, zS = a, YS(Ki, function() {
        return $u(), null;
      })));
      var p = (u.subtreeFlags & (kl | Dl | Ol | Gi)) !== De, v = (u.flags & (kl | Dl | Ol | Gi)) !== De;
      if (p || v) {
        var y = Vr.transition;
        Vr.transition = null;
        var g = Ua();
        jn(Lr);
        var b = Tt;
        Tt |= ji, kS.current = null, Hb(e, u), qC(), Jb(e, u, s), ZT(e.containerInfo), e.current = u, ds(s), e1(u, e, s), ps(), md(), Tt = b, jn(g), Vr.transition = y;
      } else
        e.current = u, qC();
      var w = nc;
      if (nc ? (nc = !1, Vo = e, Bp = s) : (Bf = 0, zm = null), f = e.pendingLanes, f === $ && (Vf = null), w || sR(e.current, !1), gd(u.stateNode, i), Xr && e.memoizedUpdaters.clear(), S1(), Va(e, Qn()), t !== null)
        for (var N = e.onRecoverableError, A = 0; A < t.length; A++) {
          var H = t[A], ue = H.stack, ze = H.digest;
          N(H.value, {
            componentStack: ue,
            digest: ze
          });
        }
      if (Mm) {
        Mm = !1;
        var be = MS;
        throw MS = null, be;
      }
      return Jr(Bp, Be) && e.tag !== Lo && $u(), f = e.pendingLanes, Jr(f, Be) ? ($x(), e === US ? Ip++ : (Ip = 0, US = e)) : Ip = 0, Mo(), Rd(), null;
    }
    function $u() {
      if (Vo !== null) {
        var e = Wv(Bp), t = ks(Na, e), a = Vr.transition, i = Ua();
        try {
          return Vr.transition = null, jn(t), B1();
        } finally {
          jn(i), Vr.transition = a;
        }
      }
      return !1;
    }
    function V1(e) {
      NS.push(e), nc || (nc = !0, YS(Ki, function() {
        return $u(), null;
      }));
    }
    function B1() {
      if (Vo === null)
        return !1;
      var e = zS;
      zS = null;
      var t = Vo, a = Bp;
      if (Vo = null, Bp = $, (Tt & (Br | ji)) !== vr)
        throw new Error("Cannot flush passive effects while already rendering.");
      AS = !0, Nm = !1, Su(a);
      var i = Tt;
      Tt |= ji, u1(t.current), r1(t, t.current, a, e);
      {
        var u = NS;
        NS = [];
        for (var s = 0; s < u.length; s++) {
          var f = u[s];
          Ib(t, f);
        }
      }
      xd(), sR(t.current, !0), Tt = i, Mo(), Nm ? t === zm ? Bf++ : (Bf = 0, zm = t) : Bf = 0, AS = !1, Nm = !1, Sd(t);
      {
        var p = t.current.stateNode;
        p.effectDuration = 0, p.passiveEffectDuration = 0;
      }
      return !0;
    }
    function lR(e) {
      return Vf !== null && Vf.has(e);
    }
    function I1(e) {
      Vf === null ? Vf = /* @__PURE__ */ new Set([e]) : Vf.add(e);
    }
    function Y1(e) {
      Mm || (Mm = !0, MS = e);
    }
    var $1 = Y1;
    function uR(e, t, a) {
      var i = Js(a, t), u = a0(e, i, Be), s = zo(e, u, Be), f = Ea();
      s !== null && (So(s, Be, f), Va(s, f));
    }
    function fn(e, t, a) {
      if (Ab(a), Wp(!1), e.tag === J) {
        uR(e, e, a);
        return;
      }
      var i = null;
      for (i = t; i !== null; ) {
        if (i.tag === J) {
          uR(i, e, a);
          return;
        } else if (i.tag === ce) {
          var u = i.type, s = i.stateNode;
          if (typeof u.getDerivedStateFromError == "function" || typeof s.componentDidCatch == "function" && !lR(s)) {
            var f = Js(a, e), p = uS(i, f, Be), v = zo(i, p, Be), y = Ea();
            v !== null && (So(v, Be, y), Va(v, y));
            return;
          }
        }
        i = i.return;
      }
      S(`Internal React error: Attempted to capture a commit phase error inside a detached tree. This indicates a bug in React. Likely causes include deleting the same fiber more than once, committing an already-finished tree, or an inconsistent return pointer.

Error message:

%s`, a);
    }
    function Q1(e, t, a) {
      var i = e.pingCache;
      i !== null && i.delete(t);
      var u = Ea();
      Jc(e, a), t_(e), Sa === e && ku(hr, a) && (mr === jp || mr === Dm && _u(hr) && Qn() - LS < W0 ? rc(e, $) : Lm = et(Lm, a)), Va(e, u);
    }
    function oR(e, t) {
      t === Dt && (t = b1(e));
      var a = Ea(), i = Fa(e, t);
      i !== null && (So(i, t, a), Va(i, a));
    }
    function W1(e) {
      var t = e.memoizedState, a = Dt;
      t !== null && (a = t.retryLane), oR(e, a);
    }
    function G1(e, t) {
      var a = Dt, i;
      switch (e.tag) {
        case ke:
          i = e.stateNode;
          var u = e.memoizedState;
          u !== null && (a = u.retryLane);
          break;
        case un:
          i = e.stateNode;
          break;
        default:
          throw new Error("Pinged unknown suspense boundary type. This is probably a bug in React.");
      }
      i !== null && i.delete(t), oR(e, a);
    }
    function K1(e) {
      return e < 120 ? 120 : e < 480 ? 480 : e < 1080 ? 1080 : e < 1920 ? 1920 : e < 3e3 ? 3e3 : e < 4320 ? 4320 : R1(e / 1960) * 1960;
    }
    function q1() {
      if (Ip > w1)
        throw Ip = 0, US = null, new Error("Maximum update depth exceeded. This can happen when a component repeatedly calls setState inside componentWillUpdate or componentDidUpdate. React limits the number of nested updates to prevent infinite loops.");
      Bf > x1 && (Bf = 0, zm = null, S("Maximum update depth exceeded. This can happen when a component calls setState inside useEffect, but useEffect either doesn't have a dependency array, or one of the dependencies changes on every render."));
    }
    function X1() {
      al.flushLegacyContextWarning(), al.flushPendingUnsafeLifecycleWarnings();
    }
    function sR(e, t) {
      Qt(e), Hm(e, _l, m1), t && Hm(e, Ti, y1), Hm(e, _l, v1), t && Hm(e, Ti, h1), cn();
    }
    function Hm(e, t, a) {
      for (var i = e, u = null; i !== null; ) {
        var s = i.subtreeFlags & t;
        i !== u && i.child !== null && s !== De ? i = i.child : ((i.flags & t) !== De && a(i), i.sibling !== null ? i = i.sibling : i = u = i.return);
      }
    }
    var Pm = null;
    function cR(e) {
      {
        if ((Tt & Br) !== vr || !(e.mode & vt))
          return;
        var t = e.tag;
        if (t !== tt && t !== J && t !== ce && t !== se && t !== Le && t !== Qe && t !== He)
          return;
        var a = We(e) || "ReactComponent";
        if (Pm !== null) {
          if (Pm.has(a))
            return;
          Pm.add(a);
        } else
          Pm = /* @__PURE__ */ new Set([a]);
        var i = ir;
        try {
          Qt(e), S("Can't perform a React state update on a component that hasn't mounted yet. This indicates that you have a side-effect in your render function that asynchronously later calls tries to update the component. Move this work to useEffect instead.");
        } finally {
          i ? Qt(e) : cn();
        }
      }
    }
    var VS;
    {
      var Z1 = null;
      VS = function(e, t, a) {
        var i = gR(Z1, t);
        try {
          return T0(e, t, a);
        } catch (s) {
          if (cx() || s !== null && typeof s == "object" && typeof s.then == "function")
            throw s;
          if (Wh(), xC(), D0(e, t), gR(t, i), t.mode & Mt && Ig(t), bl(null, T0, null, e, t, a), Qi()) {
            var u = us();
            typeof u == "object" && u !== null && u._suppressLogging && typeof s == "object" && s !== null && !s._suppressLogging && (s._suppressLogging = !0);
          }
          throw s;
        }
      };
    }
    var fR = !1, BS;
    BS = /* @__PURE__ */ new Set();
    function J1(e) {
      if (mi && !Bx())
        switch (e.tag) {
          case se:
          case Le:
          case He: {
            var t = Dn && We(Dn) || "Unknown", a = t;
            if (!BS.has(a)) {
              BS.add(a);
              var i = We(e) || "Unknown";
              S("Cannot update a component (`%s`) while rendering a different component (`%s`). To locate the bad setState() call inside `%s`, follow the stack trace as described in https://reactjs.org/link/setstate-in-render", i, t, t);
            }
            break;
          }
          case ce: {
            fR || (S("Cannot update during an existing state transition (such as within `render`). Render methods should be a pure function of props and state."), fR = !0);
            break;
          }
        }
    }
    function Qp(e, t) {
      if (Xr) {
        var a = e.memoizedUpdaters;
        a.forEach(function(i) {
          bs(e, i, t);
        });
      }
    }
    var IS = {};
    function YS(e, t) {
      {
        var a = dl.current;
        return a !== null ? (a.push(t), IS) : vd(e, t);
      }
    }
    function dR(e) {
      if (e !== IS)
        return Lv(e);
    }
    function pR() {
      return dl.current !== null;
    }
    function e_(e) {
      {
        if (e.mode & vt) {
          if (!Y0())
            return;
        } else if (!C1() || Tt !== vr || e.tag !== se && e.tag !== Le && e.tag !== He)
          return;
        if (dl.current === null) {
          var t = ir;
          try {
            Qt(e), S(`An update to %s inside a test was not wrapped in act(...).

When testing, code that causes React state updates should be wrapped into act(...):

act(() => {
  /* fire events that update state */
});
/* assert on the output */

This ensures that you're testing the behavior the user would see in the browser. Learn more at https://reactjs.org/link/wrap-tests-with-act`, We(e));
          } finally {
            t ? Qt(e) : cn();
          }
        }
      }
    }
    function t_(e) {
      e.tag !== Lo && Y0() && dl.current === null && S(`A suspended resource finished loading inside a test, but the event was not wrapped in act(...).

When testing, code that resolves suspended data should be wrapped into act(...):

act(() => {
  /* finish loading suspended data */
});
/* assert on the output */

This ensures that you're testing the behavior the user would see in the browser. Learn more at https://reactjs.org/link/wrap-tests-with-act`);
    }
    function Wp(e) {
      q0 = e;
    }
    var Fi = null, If = null, n_ = function(e) {
      Fi = e;
    };
    function Yf(e) {
      {
        if (Fi === null)
          return e;
        var t = Fi(e);
        return t === void 0 ? e : t.current;
      }
    }
    function $S(e) {
      return Yf(e);
    }
    function QS(e) {
      {
        if (Fi === null)
          return e;
        var t = Fi(e);
        if (t === void 0) {
          if (e != null && typeof e.render == "function") {
            var a = Yf(e.render);
            if (e.render !== a) {
              var i = {
                $$typeof: Y,
                render: a
              };
              return e.displayName !== void 0 && (i.displayName = e.displayName), i;
            }
          }
          return e;
        }
        return t.current;
      }
    }
    function vR(e, t) {
      {
        if (Fi === null)
          return !1;
        var a = e.elementType, i = t.type, u = !1, s = typeof i == "object" && i !== null ? i.$$typeof : null;
        switch (e.tag) {
          case ce: {
            typeof i == "function" && (u = !0);
            break;
          }
          case se: {
            (typeof i == "function" || s === Ge) && (u = !0);
            break;
          }
          case Le: {
            (s === Y || s === Ge) && (u = !0);
            break;
          }
          case Qe:
          case He: {
            (s === Ze || s === Ge) && (u = !0);
            break;
          }
          default:
            return !1;
        }
        if (u) {
          var f = Fi(a);
          if (f !== void 0 && f === Fi(i))
            return !0;
        }
        return !1;
      }
    }
    function hR(e) {
      {
        if (Fi === null || typeof WeakSet != "function")
          return;
        If === null && (If = /* @__PURE__ */ new WeakSet()), If.add(e);
      }
    }
    var r_ = function(e, t) {
      {
        if (Fi === null)
          return;
        var a = t.staleFamilies, i = t.updatedFamilies;
        $u(), Yu(function() {
          WS(e.current, i, a);
        });
      }
    }, a_ = function(e, t) {
      {
        if (e.context !== ui)
          return;
        $u(), Yu(function() {
          Gp(t, e, null, null);
        });
      }
    };
    function WS(e, t, a) {
      {
        var i = e.alternate, u = e.child, s = e.sibling, f = e.tag, p = e.type, v = null;
        switch (f) {
          case se:
          case He:
          case ce:
            v = p;
            break;
          case Le:
            v = p.render;
            break;
        }
        if (Fi === null)
          throw new Error("Expected resolveFamily to be set during hot reload.");
        var y = !1, g = !1;
        if (v !== null) {
          var b = Fi(v);
          b !== void 0 && (a.has(b) ? g = !0 : t.has(b) && (f === ce ? g = !0 : y = !0));
        }
        if (If !== null && (If.has(e) || i !== null && If.has(i)) && (g = !0), g && (e._debugNeedsRemount = !0), g || y) {
          var w = Fa(e, Be);
          w !== null && yr(w, e, Be, Zt);
        }
        u !== null && !g && WS(u, t, a), s !== null && WS(s, t, a);
      }
    }
    var i_ = function(e, t) {
      {
        var a = /* @__PURE__ */ new Set(), i = new Set(t.map(function(u) {
          return u.current;
        }));
        return GS(e.current, i, a), a;
      }
    };
    function GS(e, t, a) {
      {
        var i = e.child, u = e.sibling, s = e.tag, f = e.type, p = null;
        switch (s) {
          case se:
          case He:
          case ce:
            p = f;
            break;
          case Le:
            p = f.render;
            break;
        }
        var v = !1;
        p !== null && t.has(p) && (v = !0), v ? l_(e, a) : i !== null && GS(i, t, a), u !== null && GS(u, t, a);
      }
    }
    function l_(e, t) {
      {
        var a = u_(e, t);
        if (a)
          return;
        for (var i = e; ; ) {
          switch (i.tag) {
            case ae:
              t.add(i.stateNode);
              return;
            case Se:
              t.add(i.stateNode.containerInfo);
              return;
            case J:
              t.add(i.stateNode.containerInfo);
              return;
          }
          if (i.return === null)
            throw new Error("Expected to reach root first.");
          i = i.return;
        }
      }
    }
    function u_(e, t) {
      for (var a = e, i = !1; ; ) {
        if (a.tag === ae)
          i = !0, t.add(a.stateNode);
        else if (a.child !== null) {
          a.child.return = a, a = a.child;
          continue;
        }
        if (a === e)
          return i;
        for (; a.sibling === null; ) {
          if (a.return === null || a.return === e)
            return i;
          a = a.return;
        }
        a.sibling.return = a.return, a = a.sibling;
      }
      return !1;
    }
    var KS;
    {
      KS = !1;
      try {
        var mR = Object.preventExtensions({});
      } catch {
        KS = !0;
      }
    }
    function o_(e, t, a, i) {
      this.tag = e, this.key = a, this.elementType = null, this.type = null, this.stateNode = null, this.return = null, this.child = null, this.sibling = null, this.index = 0, this.ref = null, this.pendingProps = t, this.memoizedProps = null, this.updateQueue = null, this.memoizedState = null, this.dependencies = null, this.mode = i, this.flags = De, this.subtreeFlags = De, this.deletions = null, this.lanes = $, this.childLanes = $, this.alternate = null, this.actualDuration = Number.NaN, this.actualStartTime = Number.NaN, this.selfBaseDuration = Number.NaN, this.treeBaseDuration = Number.NaN, this.actualDuration = 0, this.actualStartTime = -1, this.selfBaseDuration = 0, this.treeBaseDuration = 0, this._debugSource = null, this._debugOwner = null, this._debugNeedsRemount = !1, this._debugHookTypes = null, !KS && typeof Object.preventExtensions == "function" && Object.preventExtensions(this);
    }
    var oi = function(e, t, a, i) {
      return new o_(e, t, a, i);
    };
    function qS(e) {
      var t = e.prototype;
      return !!(t && t.isReactComponent);
    }
    function s_(e) {
      return typeof e == "function" && !qS(e) && e.defaultProps === void 0;
    }
    function c_(e) {
      if (typeof e == "function")
        return qS(e) ? ce : se;
      if (e != null) {
        var t = e.$$typeof;
        if (t === Y)
          return Le;
        if (t === Ze)
          return Qe;
      }
      return tt;
    }
    function ic(e, t) {
      var a = e.alternate;
      a === null ? (a = oi(e.tag, t, e.key, e.mode), a.elementType = e.elementType, a.type = e.type, a.stateNode = e.stateNode, a._debugSource = e._debugSource, a._debugOwner = e._debugOwner, a._debugHookTypes = e._debugHookTypes, a.alternate = e, e.alternate = a) : (a.pendingProps = t, a.type = e.type, a.flags = De, a.subtreeFlags = De, a.deletions = null, a.actualDuration = 0, a.actualStartTime = -1), a.flags = e.flags & zn, a.childLanes = e.childLanes, a.lanes = e.lanes, a.child = e.child, a.memoizedProps = e.memoizedProps, a.memoizedState = e.memoizedState, a.updateQueue = e.updateQueue;
      var i = e.dependencies;
      switch (a.dependencies = i === null ? null : {
        lanes: i.lanes,
        firstContext: i.firstContext
      }, a.sibling = e.sibling, a.index = e.index, a.ref = e.ref, a.selfBaseDuration = e.selfBaseDuration, a.treeBaseDuration = e.treeBaseDuration, a._debugNeedsRemount = e._debugNeedsRemount, a.tag) {
        case tt:
        case se:
        case He:
          a.type = Yf(e.type);
          break;
        case ce:
          a.type = $S(e.type);
          break;
        case Le:
          a.type = QS(e.type);
          break;
      }
      return a;
    }
    function f_(e, t) {
      e.flags &= zn | mn;
      var a = e.alternate;
      if (a === null)
        e.childLanes = $, e.lanes = t, e.child = null, e.subtreeFlags = De, e.memoizedProps = null, e.memoizedState = null, e.updateQueue = null, e.dependencies = null, e.stateNode = null, e.selfBaseDuration = 0, e.treeBaseDuration = 0;
      else {
        e.childLanes = a.childLanes, e.lanes = a.lanes, e.child = a.child, e.subtreeFlags = De, e.deletions = null, e.memoizedProps = a.memoizedProps, e.memoizedState = a.memoizedState, e.updateQueue = a.updateQueue, e.type = a.type;
        var i = a.dependencies;
        e.dependencies = i === null ? null : {
          lanes: i.lanes,
          firstContext: i.firstContext
        }, e.selfBaseDuration = a.selfBaseDuration, e.treeBaseDuration = a.treeBaseDuration;
      }
      return e;
    }
    function d_(e, t, a) {
      var i;
      return e === jh ? (i = vt, t === !0 && (i |= Kt, i |= Nt)) : i = Oe, Xr && (i |= Mt), oi(J, null, null, i);
    }
    function XS(e, t, a, i, u, s) {
      var f = tt, p = e;
      if (typeof e == "function")
        qS(e) ? (f = ce, p = $S(p)) : p = Yf(p);
      else if (typeof e == "string")
        f = ae;
      else
        e: switch (e) {
          case di:
            return Yo(a.children, u, s, t);
          case Wa:
            f = ct, u |= Kt, (u & vt) !== Oe && (u |= Nt);
            break;
          case pi:
            return p_(a, u, s, t);
          case ie:
            return v_(a, u, s, t);
          case he:
            return h_(a, u, s, t);
          case Tn:
            return yR(a, u, s, t);
          case nn:
          case ht:
          case sn:
          case ar:
          case pt:
          default: {
            if (typeof e == "object" && e !== null)
              switch (e.$$typeof) {
                case vi:
                  f = qe;
                  break e;
                case R:
                  f = gt;
                  break e;
                case Y:
                  f = Le, p = QS(p);
                  break e;
                case Ze:
                  f = Qe;
                  break e;
                case Ge:
                  f = ln, p = null;
                  break e;
              }
            var v = "";
            {
              (e === void 0 || typeof e == "object" && e !== null && Object.keys(e).length === 0) && (v += " You likely forgot to export your component from the file it's defined in, or you might have mixed up default and named imports.");
              var y = i ? We(i) : null;
              y && (v += `

Check the render method of \`` + y + "`.");
            }
            throw new Error("Element type is invalid: expected a string (for built-in components) or a class/function (for composite components) " + ("but got: " + (e == null ? e : typeof e) + "." + v));
          }
        }
      var g = oi(f, a, t, u);
      return g.elementType = e, g.type = p, g.lanes = s, g._debugOwner = i, g;
    }
    function ZS(e, t, a) {
      var i = null;
      i = e._owner;
      var u = e.type, s = e.key, f = e.props, p = XS(u, s, f, i, t, a);
      return p._debugSource = e._source, p._debugOwner = e._owner, p;
    }
    function Yo(e, t, a, i) {
      var u = oi(at, e, i, t);
      return u.lanes = a, u;
    }
    function p_(e, t, a, i) {
      typeof e.id != "string" && S('Profiler must specify an "id" of type `string` as a prop. Received the type `%s` instead.', typeof e.id);
      var u = oi(it, e, i, t | Mt);
      return u.elementType = pi, u.lanes = a, u.stateNode = {
        effectDuration: 0,
        passiveEffectDuration: 0
      }, u;
    }
    function v_(e, t, a, i) {
      var u = oi(ke, e, i, t);
      return u.elementType = ie, u.lanes = a, u;
    }
    function h_(e, t, a, i) {
      var u = oi(un, e, i, t);
      return u.elementType = he, u.lanes = a, u;
    }
    function yR(e, t, a, i) {
      var u = oi(Me, e, i, t);
      u.elementType = Tn, u.lanes = a;
      var s = {
        isHidden: !1
      };
      return u.stateNode = s, u;
    }
    function JS(e, t, a) {
      var i = oi(Ve, e, null, t);
      return i.lanes = a, i;
    }
    function m_() {
      var e = oi(ae, null, null, Oe);
      return e.elementType = "DELETED", e;
    }
    function y_(e) {
      var t = oi(Jt, null, null, Oe);
      return t.stateNode = e, t;
    }
    function eE(e, t, a) {
      var i = e.children !== null ? e.children : [], u = oi(Se, i, e.key, t);
      return u.lanes = a, u.stateNode = {
        containerInfo: e.containerInfo,
        pendingChildren: null,
        // Used by persistent updates
        implementation: e.implementation
      }, u;
    }
    function gR(e, t) {
      return e === null && (e = oi(tt, null, null, Oe)), e.tag = t.tag, e.key = t.key, e.elementType = t.elementType, e.type = t.type, e.stateNode = t.stateNode, e.return = t.return, e.child = t.child, e.sibling = t.sibling, e.index = t.index, e.ref = t.ref, e.pendingProps = t.pendingProps, e.memoizedProps = t.memoizedProps, e.updateQueue = t.updateQueue, e.memoizedState = t.memoizedState, e.dependencies = t.dependencies, e.mode = t.mode, e.flags = t.flags, e.subtreeFlags = t.subtreeFlags, e.deletions = t.deletions, e.lanes = t.lanes, e.childLanes = t.childLanes, e.alternate = t.alternate, e.actualDuration = t.actualDuration, e.actualStartTime = t.actualStartTime, e.selfBaseDuration = t.selfBaseDuration, e.treeBaseDuration = t.treeBaseDuration, e._debugSource = t._debugSource, e._debugOwner = t._debugOwner, e._debugNeedsRemount = t._debugNeedsRemount, e._debugHookTypes = t._debugHookTypes, e;
    }
    function g_(e, t, a, i, u) {
      this.tag = t, this.containerInfo = e, this.pendingChildren = null, this.current = null, this.pingCache = null, this.finishedWork = null, this.timeoutHandle = Uy, this.context = null, this.pendingContext = null, this.callbackNode = null, this.callbackPriority = Dt, this.eventTimes = xs($), this.expirationTimes = xs(Zt), this.pendingLanes = $, this.suspendedLanes = $, this.pingedLanes = $, this.expiredLanes = $, this.mutableReadLanes = $, this.finishedLanes = $, this.entangledLanes = $, this.entanglements = xs($), this.identifierPrefix = i, this.onRecoverableError = u, this.mutableSourceEagerHydrationData = null, this.effectDuration = 0, this.passiveEffectDuration = 0;
      {
        this.memoizedUpdaters = /* @__PURE__ */ new Set();
        for (var s = this.pendingUpdatersLaneMap = [], f = 0; f < Cu; f++)
          s.push(/* @__PURE__ */ new Set());
      }
      switch (t) {
        case jh:
          this._debugRootType = a ? "hydrateRoot()" : "createRoot()";
          break;
        case Lo:
          this._debugRootType = a ? "hydrate()" : "render()";
          break;
      }
    }
    function SR(e, t, a, i, u, s, f, p, v, y) {
      var g = new g_(e, t, a, p, v), b = d_(t, s);
      g.current = b, b.stateNode = g;
      {
        var w = {
          element: i,
          isDehydrated: a,
          cache: null,
          // not enabled yet
          transitions: null,
          pendingSuspenseBoundaries: null
        };
        b.memoizedState = w;
      }
      return pg(b), g;
    }
    var tE = "18.3.1";
    function S_(e, t, a) {
      var i = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : null;
      return Yr(i), {
        // This tag allow us to uniquely identify this as a React Portal
        $$typeof: rr,
        key: i == null ? null : "" + i,
        children: e,
        containerInfo: t,
        implementation: a
      };
    }
    var nE, rE;
    nE = !1, rE = {};
    function ER(e) {
      if (!e)
        return ui;
      var t = po(e), a = tx(t);
      if (t.tag === ce) {
        var i = t.type;
        if (Yl(i))
          return WE(t, i, a);
      }
      return a;
    }
    function E_(e, t) {
      {
        var a = po(e);
        if (a === void 0) {
          if (typeof e.render == "function")
            throw new Error("Unable to find node on an unmounted component.");
          var i = Object.keys(e).join(",");
          throw new Error("Argument appears to not be a ReactComponent. Keys: " + i);
        }
        var u = Kr(a);
        if (u === null)
          return null;
        if (u.mode & Kt) {
          var s = We(a) || "Component";
          if (!rE[s]) {
            rE[s] = !0;
            var f = ir;
            try {
              Qt(u), a.mode & Kt ? S("%s is deprecated in StrictMode. %s was passed an instance of %s which is inside StrictMode. Instead, add a ref directly to the element you want to reference. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-find-node", t, t, s) : S("%s is deprecated in StrictMode. %s was passed an instance of %s which renders StrictMode children. Instead, add a ref directly to the element you want to reference. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-find-node", t, t, s);
            } finally {
              f ? Qt(f) : cn();
            }
          }
        }
        return u.stateNode;
      }
    }
    function CR(e, t, a, i, u, s, f, p) {
      var v = !1, y = null;
      return SR(e, t, v, y, a, i, u, s, f);
    }
    function RR(e, t, a, i, u, s, f, p, v, y) {
      var g = !0, b = SR(a, i, g, e, u, s, f, p, v);
      b.context = ER(null);
      var w = b.current, N = Ea(), A = Bo(w), H = Pu(N, A);
      return H.callback = t ?? null, zo(w, H, A), _1(b, A, N), b;
    }
    function Gp(e, t, a, i) {
      yd(t, e);
      var u = t.current, s = Ea(), f = Bo(u);
      gn(f);
      var p = ER(a);
      t.context === null ? t.context = p : t.pendingContext = p, mi && ir !== null && !nE && (nE = !0, S(`Render methods should be a pure function of props and state; triggering nested component updates from render is not allowed. If necessary, trigger nested updates in componentDidUpdate.

Check the render method of %s.`, We(ir) || "Unknown"));
      var v = Pu(s, f);
      v.payload = {
        element: e
      }, i = i === void 0 ? null : i, i !== null && (typeof i != "function" && S("render(...): Expected the last optional `callback` argument to be a function. Instead received: %s.", i), v.callback = i);
      var y = zo(u, v, f);
      return y !== null && (yr(y, u, f, s), Zh(y, u, f)), f;
    }
    function Vm(e) {
      var t = e.current;
      if (!t.child)
        return null;
      switch (t.child.tag) {
        case ae:
          return t.child.stateNode;
        default:
          return t.child.stateNode;
      }
    }
    function C_(e) {
      switch (e.tag) {
        case J: {
          var t = e.stateNode;
          if (tf(t)) {
            var a = jv(t);
            L1(t, a);
          }
          break;
        }
        case ke: {
          Yu(function() {
            var u = Fa(e, Be);
            if (u !== null) {
              var s = Ea();
              yr(u, e, Be, s);
            }
          });
          var i = Be;
          aE(e, i);
          break;
        }
      }
    }
    function TR(e, t) {
      var a = e.memoizedState;
      a !== null && a.dehydrated !== null && (a.retryLane = Bv(a.retryLane, t));
    }
    function aE(e, t) {
      TR(e, t);
      var a = e.alternate;
      a && TR(a, t);
    }
    function R_(e) {
      if (e.tag === ke) {
        var t = Ss, a = Fa(e, t);
        if (a !== null) {
          var i = Ea();
          yr(a, e, t, i);
        }
        aE(e, t);
      }
    }
    function T_(e) {
      if (e.tag === ke) {
        var t = Bo(e), a = Fa(e, t);
        if (a !== null) {
          var i = Ea();
          yr(a, e, t, i);
        }
        aE(e, t);
      }
    }
    function wR(e) {
      var t = dn(e);
      return t === null ? null : t.stateNode;
    }
    var xR = function(e) {
      return null;
    };
    function w_(e) {
      return xR(e);
    }
    var bR = function(e) {
      return !1;
    };
    function x_(e) {
      return bR(e);
    }
    var _R = null, kR = null, DR = null, OR = null, LR = null, MR = null, NR = null, zR = null, UR = null;
    {
      var AR = function(e, t, a) {
        var i = t[a], u = st(e) ? e.slice() : rt({}, e);
        return a + 1 === t.length ? (st(u) ? u.splice(i, 1) : delete u[i], u) : (u[i] = AR(e[i], t, a + 1), u);
      }, jR = function(e, t) {
        return AR(e, t, 0);
      }, FR = function(e, t, a, i) {
        var u = t[i], s = st(e) ? e.slice() : rt({}, e);
        if (i + 1 === t.length) {
          var f = a[i];
          s[f] = s[u], st(s) ? s.splice(u, 1) : delete s[u];
        } else
          s[u] = FR(
            // $FlowFixMe number or string is fine here
            e[u],
            t,
            a,
            i + 1
          );
        return s;
      }, HR = function(e, t, a) {
        if (t.length !== a.length) {
          Ee("copyWithRename() expects paths of the same length");
          return;
        } else
          for (var i = 0; i < a.length - 1; i++)
            if (t[i] !== a[i]) {
              Ee("copyWithRename() expects paths to be the same except for the deepest key");
              return;
            }
        return FR(e, t, a, 0);
      }, PR = function(e, t, a, i) {
        if (a >= t.length)
          return i;
        var u = t[a], s = st(e) ? e.slice() : rt({}, e);
        return s[u] = PR(e[u], t, a + 1, i), s;
      }, VR = function(e, t, a) {
        return PR(e, t, 0, a);
      }, iE = function(e, t) {
        for (var a = e.memoizedState; a !== null && t > 0; )
          a = a.next, t--;
        return a;
      };
      _R = function(e, t, a, i) {
        var u = iE(e, t);
        if (u !== null) {
          var s = VR(u.memoizedState, a, i);
          u.memoizedState = s, u.baseState = s, e.memoizedProps = rt({}, e.memoizedProps);
          var f = Fa(e, Be);
          f !== null && yr(f, e, Be, Zt);
        }
      }, kR = function(e, t, a) {
        var i = iE(e, t);
        if (i !== null) {
          var u = jR(i.memoizedState, a);
          i.memoizedState = u, i.baseState = u, e.memoizedProps = rt({}, e.memoizedProps);
          var s = Fa(e, Be);
          s !== null && yr(s, e, Be, Zt);
        }
      }, DR = function(e, t, a, i) {
        var u = iE(e, t);
        if (u !== null) {
          var s = HR(u.memoizedState, a, i);
          u.memoizedState = s, u.baseState = s, e.memoizedProps = rt({}, e.memoizedProps);
          var f = Fa(e, Be);
          f !== null && yr(f, e, Be, Zt);
        }
      }, OR = function(e, t, a) {
        e.pendingProps = VR(e.memoizedProps, t, a), e.alternate && (e.alternate.pendingProps = e.pendingProps);
        var i = Fa(e, Be);
        i !== null && yr(i, e, Be, Zt);
      }, LR = function(e, t) {
        e.pendingProps = jR(e.memoizedProps, t), e.alternate && (e.alternate.pendingProps = e.pendingProps);
        var a = Fa(e, Be);
        a !== null && yr(a, e, Be, Zt);
      }, MR = function(e, t, a) {
        e.pendingProps = HR(e.memoizedProps, t, a), e.alternate && (e.alternate.pendingProps = e.pendingProps);
        var i = Fa(e, Be);
        i !== null && yr(i, e, Be, Zt);
      }, NR = function(e) {
        var t = Fa(e, Be);
        t !== null && yr(t, e, Be, Zt);
      }, zR = function(e) {
        xR = e;
      }, UR = function(e) {
        bR = e;
      };
    }
    function b_(e) {
      var t = Kr(e);
      return t === null ? null : t.stateNode;
    }
    function __(e) {
      return null;
    }
    function k_() {
      return ir;
    }
    function D_(e) {
      var t = e.findFiberByHostInstance, a = k.ReactCurrentDispatcher;
      return mo({
        bundleType: e.bundleType,
        version: e.version,
        rendererPackageName: e.rendererPackageName,
        rendererConfig: e.rendererConfig,
        overrideHookState: _R,
        overrideHookStateDeletePath: kR,
        overrideHookStateRenamePath: DR,
        overrideProps: OR,
        overridePropsDeletePath: LR,
        overridePropsRenamePath: MR,
        setErrorHandler: zR,
        setSuspenseHandler: UR,
        scheduleUpdate: NR,
        currentDispatcherRef: a,
        findHostInstanceByFiber: b_,
        findFiberByHostInstance: t || __,
        // React Refresh
        findHostInstancesForRefresh: i_,
        scheduleRefresh: r_,
        scheduleRoot: a_,
        setRefreshHandler: n_,
        // Enables DevTools to append owner stacks to error messages in DEV mode.
        getCurrentFiber: k_,
        // Enables DevTools to detect reconciler version rather than renderer version
        // which may not match for third party renderers.
        reconcilerVersion: tE
      });
    }
    var BR = typeof reportError == "function" ? (
      // In modern browsers, reportError will dispatch an error event,
      // emulating an uncaught JavaScript error.
      reportError
    ) : function(e) {
      console.error(e);
    };
    function lE(e) {
      this._internalRoot = e;
    }
    Bm.prototype.render = lE.prototype.render = function(e) {
      var t = this._internalRoot;
      if (t === null)
        throw new Error("Cannot update an unmounted root.");
      {
        typeof arguments[1] == "function" ? S("render(...): does not support the second callback argument. To execute a side effect after rendering, declare it in a component body with useEffect().") : Im(arguments[1]) ? S("You passed a container to the second argument of root.render(...). You don't need to pass it again since you already passed it to create the root.") : typeof arguments[1] < "u" && S("You passed a second argument to root.render(...) but it only accepts one argument.");
        var a = t.containerInfo;
        if (a.nodeType !== Mn) {
          var i = wR(t.current);
          i && i.parentNode !== a && S("render(...): It looks like the React-rendered content of the root container was removed without using React. This is not supported and will cause errors. Instead, call root.unmount() to empty a root's container.");
        }
      }
      Gp(e, t, null, null);
    }, Bm.prototype.unmount = lE.prototype.unmount = function() {
      typeof arguments[0] == "function" && S("unmount(...): does not support a callback argument. To execute a side effect after rendering, declare it in a component body with useEffect().");
      var e = this._internalRoot;
      if (e !== null) {
        this._internalRoot = null;
        var t = e.containerInfo;
        eR() && S("Attempted to synchronously unmount a root while React was already rendering. React cannot finish unmounting the root until the current render has completed, which may lead to a race condition."), Yu(function() {
          Gp(null, e, null, null);
        }), BE(t);
      }
    };
    function O_(e, t) {
      if (!Im(e))
        throw new Error("createRoot(...): Target container is not a DOM element.");
      IR(e);
      var a = !1, i = !1, u = "", s = BR;
      t != null && (t.hydrate ? Ee("hydrate through createRoot is deprecated. Use ReactDOMClient.hydrateRoot(container, <App />) instead.") : typeof t == "object" && t !== null && t.$$typeof === _r && S(`You passed a JSX element to createRoot. You probably meant to call root.render instead. Example usage:

  let root = createRoot(domContainer);
  root.render(<App />);`), t.unstable_strictMode === !0 && (a = !0), t.identifierPrefix !== void 0 && (u = t.identifierPrefix), t.onRecoverableError !== void 0 && (s = t.onRecoverableError), t.transitionCallbacks !== void 0 && t.transitionCallbacks);
      var f = CR(e, jh, null, a, i, u, s);
      Oh(f.current, e);
      var p = e.nodeType === Mn ? e.parentNode : e;
      return ep(p), new lE(f);
    }
    function Bm(e) {
      this._internalRoot = e;
    }
    function L_(e) {
      e && Zv(e);
    }
    Bm.prototype.unstable_scheduleHydration = L_;
    function M_(e, t, a) {
      if (!Im(e))
        throw new Error("hydrateRoot(...): Target container is not a DOM element.");
      IR(e), t === void 0 && S("Must provide initial children as second argument to hydrateRoot. Example usage: hydrateRoot(domContainer, <App />)");
      var i = a ?? null, u = a != null && a.hydratedSources || null, s = !1, f = !1, p = "", v = BR;
      a != null && (a.unstable_strictMode === !0 && (s = !0), a.identifierPrefix !== void 0 && (p = a.identifierPrefix), a.onRecoverableError !== void 0 && (v = a.onRecoverableError));
      var y = RR(t, null, e, jh, i, s, f, p, v);
      if (Oh(y.current, e), ep(e), u)
        for (var g = 0; g < u.length; g++) {
          var b = u[g];
          Ax(y, b);
        }
      return new Bm(y);
    }
    function Im(e) {
      return !!(e && (e.nodeType === Qr || e.nodeType === $i || e.nodeType === nd));
    }
    function Kp(e) {
      return !!(e && (e.nodeType === Qr || e.nodeType === $i || e.nodeType === nd || e.nodeType === Mn && e.nodeValue === " react-mount-point-unstable "));
    }
    function IR(e) {
      e.nodeType === Qr && e.tagName && e.tagName.toUpperCase() === "BODY" && S("createRoot(): Creating roots directly with document.body is discouraged, since its children are often manipulated by third-party scripts and browser extensions. This may lead to subtle reconciliation issues. Try using a container element created for your app."), fp(e) && (e._reactRootContainer ? S("You are calling ReactDOMClient.createRoot() on a container that was previously passed to ReactDOM.render(). This is not supported.") : S("You are calling ReactDOMClient.createRoot() on a container that has already been passed to createRoot() before. Instead, call root.render() on the existing root instead if you want to update it."));
    }
    var N_ = k.ReactCurrentOwner, YR;
    YR = function(e) {
      if (e._reactRootContainer && e.nodeType !== Mn) {
        var t = wR(e._reactRootContainer.current);
        t && t.parentNode !== e && S("render(...): It looks like the React-rendered content of this container was removed without using React. This is not supported and will cause errors. Instead, call ReactDOM.unmountComponentAtNode to empty a container.");
      }
      var a = !!e._reactRootContainer, i = uE(e), u = !!(i && Do(i));
      u && !a && S("render(...): Replacing React-rendered children with a new root component. If you intended to update the children of this node, you should instead have the existing children update their state and render the new components instead of calling ReactDOM.render."), e.nodeType === Qr && e.tagName && e.tagName.toUpperCase() === "BODY" && S("render(): Rendering components directly into document.body is discouraged, since its children are often manipulated by third-party scripts and browser extensions. This may lead to subtle reconciliation issues. Try rendering into a container element created for your app.");
    };
    function uE(e) {
      return e ? e.nodeType === $i ? e.documentElement : e.firstChild : null;
    }
    function $R() {
    }
    function z_(e, t, a, i, u) {
      if (u) {
        if (typeof i == "function") {
          var s = i;
          i = function() {
            var w = Vm(f);
            s.call(w);
          };
        }
        var f = RR(
          t,
          i,
          e,
          Lo,
          null,
          // hydrationCallbacks
          !1,
          // isStrictMode
          !1,
          // concurrentUpdatesByDefaultOverride,
          "",
          // identifierPrefix
          $R
        );
        e._reactRootContainer = f, Oh(f.current, e);
        var p = e.nodeType === Mn ? e.parentNode : e;
        return ep(p), Yu(), f;
      } else {
        for (var v; v = e.lastChild; )
          e.removeChild(v);
        if (typeof i == "function") {
          var y = i;
          i = function() {
            var w = Vm(g);
            y.call(w);
          };
        }
        var g = CR(
          e,
          Lo,
          null,
          // hydrationCallbacks
          !1,
          // isStrictMode
          !1,
          // concurrentUpdatesByDefaultOverride,
          "",
          // identifierPrefix
          $R
        );
        e._reactRootContainer = g, Oh(g.current, e);
        var b = e.nodeType === Mn ? e.parentNode : e;
        return ep(b), Yu(function() {
          Gp(t, g, a, i);
        }), g;
      }
    }
    function U_(e, t) {
      e !== null && typeof e != "function" && S("%s(...): Expected the last optional `callback` argument to be a function. Instead received: %s.", t, e);
    }
    function Ym(e, t, a, i, u) {
      YR(a), U_(u === void 0 ? null : u, "render");
      var s = a._reactRootContainer, f;
      if (!s)
        f = z_(a, t, e, u, i);
      else {
        if (f = s, typeof u == "function") {
          var p = u;
          u = function() {
            var v = Vm(f);
            p.call(v);
          };
        }
        Gp(t, f, e, u);
      }
      return Vm(f);
    }
    var QR = !1;
    function A_(e) {
      {
        QR || (QR = !0, S("findDOMNode is deprecated and will be removed in the next major release. Instead, add a ref directly to the element you want to reference. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-find-node"));
        var t = N_.current;
        if (t !== null && t.stateNode !== null) {
          var a = t.stateNode._warnedAboutRefsInRender;
          a || S("%s is accessing findDOMNode inside its render(). render() should be a pure function of props and state. It should never access something that requires stale data from the previous render, such as refs. Move this logic to componentDidMount and componentDidUpdate instead.", xt(t.type) || "A component"), t.stateNode._warnedAboutRefsInRender = !0;
        }
      }
      return e == null ? null : e.nodeType === Qr ? e : E_(e, "findDOMNode");
    }
    function j_(e, t, a) {
      if (S("ReactDOM.hydrate is no longer supported in React 18. Use hydrateRoot instead. Until you switch to the new API, your app will behave as if it's running React 17. Learn more: https://reactjs.org/link/switch-to-createroot"), !Kp(t))
        throw new Error("Target container is not a DOM element.");
      {
        var i = fp(t) && t._reactRootContainer === void 0;
        i && S("You are calling ReactDOM.hydrate() on a container that was previously passed to ReactDOMClient.createRoot(). This is not supported. Did you mean to call hydrateRoot(container, element)?");
      }
      return Ym(null, e, t, !0, a);
    }
    function F_(e, t, a) {
      if (S("ReactDOM.render is no longer supported in React 18. Use createRoot instead. Until you switch to the new API, your app will behave as if it's running React 17. Learn more: https://reactjs.org/link/switch-to-createroot"), !Kp(t))
        throw new Error("Target container is not a DOM element.");
      {
        var i = fp(t) && t._reactRootContainer === void 0;
        i && S("You are calling ReactDOM.render() on a container that was previously passed to ReactDOMClient.createRoot(). This is not supported. Did you mean to call root.render(element)?");
      }
      return Ym(null, e, t, !1, a);
    }
    function H_(e, t, a, i) {
      if (S("ReactDOM.unstable_renderSubtreeIntoContainer() is no longer supported in React 18. Consider using a portal instead. Until you switch to the createRoot API, your app will behave as if it's running React 17. Learn more: https://reactjs.org/link/switch-to-createroot"), !Kp(a))
        throw new Error("Target container is not a DOM element.");
      if (e == null || !ay(e))
        throw new Error("parentComponent must be a valid React Component");
      return Ym(e, t, a, !1, i);
    }
    var WR = !1;
    function P_(e) {
      if (WR || (WR = !0, S("unmountComponentAtNode is deprecated and will be removed in the next major release. Switch to the createRoot API. Learn more: https://reactjs.org/link/switch-to-createroot")), !Kp(e))
        throw new Error("unmountComponentAtNode(...): Target container is not a DOM element.");
      {
        var t = fp(e) && e._reactRootContainer === void 0;
        t && S("You are calling ReactDOM.unmountComponentAtNode() on a container that was previously passed to ReactDOMClient.createRoot(). This is not supported. Did you mean to call root.unmount()?");
      }
      if (e._reactRootContainer) {
        {
          var a = uE(e), i = a && !Do(a);
          i && S("unmountComponentAtNode(): The node you're attempting to unmount was rendered by another copy of React.");
        }
        return Yu(function() {
          Ym(null, null, e, !1, function() {
            e._reactRootContainer = null, BE(e);
          });
        }), !0;
      } else {
        {
          var u = uE(e), s = !!(u && Do(u)), f = e.nodeType === Qr && Kp(e.parentNode) && !!e.parentNode._reactRootContainer;
          s && S("unmountComponentAtNode(): The node you're attempting to unmount was rendered by React and is not a top-level container. %s", f ? "You may have accidentally passed in a React root node instead of its container." : "Instead, have the parent component update its state and rerender in order to remove this component.");
        }
        return !1;
      }
    }
    Tr(C_), Eo(R_), Gv(T_), Os(Ua), jd($v), (typeof Map != "function" || // $FlowIssue Flow incorrectly thinks Map has no prototype
    Map.prototype == null || typeof Map.prototype.forEach != "function" || typeof Set != "function" || // $FlowIssue Flow incorrectly thinks Set has no prototype
    Set.prototype == null || typeof Set.prototype.clear != "function" || typeof Set.prototype.forEach != "function") && S("React depends on Map and Set built-in types. Make sure that you load a polyfill in older browsers. https://reactjs.org/link/react-polyfills"), gc(BT), ry(FS, M1, Yu);
    function V_(e, t) {
      var a = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : null;
      if (!Im(t))
        throw new Error("Target container is not a DOM element.");
      return S_(e, t, null, a);
    }
    function B_(e, t, a, i) {
      return H_(e, t, a, i);
    }
    var oE = {
      usingClientEntryPoint: !1,
      // Keep in sync with ReactTestUtils.js.
      // This is an array for better minification.
      Events: [Do, Cf, Lh, oo, Sc, FS]
    };
    function I_(e, t) {
      return oE.usingClientEntryPoint || S('You are importing createRoot from "react-dom" which is not supported. You should instead import it from "react-dom/client".'), O_(e, t);
    }
    function Y_(e, t, a) {
      return oE.usingClientEntryPoint || S('You are importing hydrateRoot from "react-dom" which is not supported. You should instead import it from "react-dom/client".'), M_(e, t, a);
    }
    function $_(e) {
      return eR() && S("flushSync was called from inside a lifecycle method. React cannot flush when React is already rendering. Consider moving this call to a scheduler task or micro task."), Yu(e);
    }
    var Q_ = D_({
      findFiberByHostInstance: Ys,
      bundleType: 1,
      version: tE,
      rendererPackageName: "react-dom"
    });
    if (!Q_ && On && window.top === window.self && (navigator.userAgent.indexOf("Chrome") > -1 && navigator.userAgent.indexOf("Edge") === -1 || navigator.userAgent.indexOf("Firefox") > -1)) {
      var GR = window.location.protocol;
      /^(https?|file):$/.test(GR) && console.info("%cDownload the React DevTools for a better development experience: https://reactjs.org/link/react-devtools" + (GR === "file:" ? `
You might need to use a local HTTP server (instead of file://): https://reactjs.org/link/react-devtools-faq` : ""), "font-weight:bold");
    }
    Ia.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = oE, Ia.createPortal = V_, Ia.createRoot = I_, Ia.findDOMNode = A_, Ia.flushSync = $_, Ia.hydrate = j_, Ia.hydrateRoot = Y_, Ia.render = F_, Ia.unmountComponentAtNode = P_, Ia.unstable_batchedUpdates = FS, Ia.unstable_renderSubtreeIntoContainer = B_, Ia.version = tE, typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u" && typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop == "function" && __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop(new Error());
  }()), Ia;
}
function uT() {
  if (!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ > "u" || typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE != "function")) {
    if (process.env.NODE_ENV !== "production")
      throw new Error("^_^");
    try {
      __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(uT);
    } catch (I) {
      console.error(I);
    }
  }
}
process.env.NODE_ENV === "production" ? (uT(), pE.exports = rk()) : pE.exports = ak();
var ik = pE.exports, vE, Qm = ik;
if (process.env.NODE_ENV === "production")
  vE = Qm.createRoot, Qm.hydrateRoot;
else {
  var aT = Qm.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED;
  vE = function(I, j) {
    aT.usingClientEntryPoint = !0;
    try {
      return Qm.createRoot(I, j);
    } finally {
      aT.usingClientEntryPoint = !1;
    }
  };
}
function lk({ title: I, subtitle: j, status: k }) {
  return /* @__PURE__ */ jt.jsxs("header", { className: "chat-header", children: [
    /* @__PURE__ */ jt.jsxs("div", { className: "header-text", children: [
      /* @__PURE__ */ jt.jsx("p", { className: "chat-title", children: I }),
      j && /* @__PURE__ */ jt.jsx("p", { className: "chat-subtitle", children: j })
    ] }),
    (k == null ? void 0 : k.label) && /* @__PURE__ */ jt.jsx("span", { className: "chat-status-label", children: k.label })
  ] });
}
function uk({ role: I, text: j }) {
  return /* @__PURE__ */ jt.jsx("div", { className: `bubble ${I}`, children: j });
}
function ok({ messages: I }) {
  return /* @__PURE__ */ jt.jsx("div", { className: "chat-messages", children: I.map((j, k) => /* @__PURE__ */ jt.jsx(uk, { role: j.role, text: j.text }, k)) });
}
function sk({ options: I, onSelect: j }) {
  return /* @__PURE__ */ jt.jsx("div", { className: "options-container", children: I.map((k) => /* @__PURE__ */ jt.jsx(
    "span",
    {
      className: "option-chip",
      onClick: () => j(k),
      children: k.label
    },
    k.id
  )) });
}
function ck({ value: I, onChange: j, onSend: k, strings: Te }) {
  const Fe = (Te == null ? void 0 : Te.messagePlaceholder) || "Escribe un mensaje...", Ee = (Te == null ? void 0 : Te.sendLabel) || "Enviar";
  return /* @__PURE__ */ jt.jsxs("div", { className: "chat-input", children: [
    /* @__PURE__ */ jt.jsx(
      "input",
      {
        value: I,
        onChange: (S) => j(S.target.value),
        placeholder: Fe
      }
    ),
    /* @__PURE__ */ jt.jsx("button", { onClick: k, "aria-label": Ee, children: Ee })
  ] });
}
function fk() {
  return /* @__PURE__ */ jt.jsxs("div", { className: "typing-indicator", children: [
    /* @__PURE__ */ jt.jsx("span", {}),
    /* @__PURE__ */ jt.jsx("span", {}),
    /* @__PURE__ */ jt.jsx("span", {})
  ] });
}
function dk({ apiUrl: I, apiKey: j, widgetToken: k, tenantId: Te, tenantTheme: Fe, strings: Ee }) {
  const [S, Et] = Ya.useState([]), [se, ce] = Ya.useState([]), [tt, J] = Ya.useState(""), [Se, ae] = Ya.useState(!1), Ve = Ya.useRef(null), at = Ya.useRef(null);
  Ya.useEffect(() => {
    var qe;
    let gt = localStorage.getItem("session_id");
    !gt && ((qe = window.crypto) != null && qe.randomUUID) ? (gt = window.crypto.randomUUID(), localStorage.setItem("session_id", gt)) : gt || (gt = `${Date.now()}-${Math.random().toString(16).slice(2)}`, localStorage.setItem("session_id", gt)), at.current = gt;
  }, []), Ya.useEffect(() => {
    Ve.current && (Ve.current.scrollTop = Ve.current.scrollHeight);
  }, [S, Se]);
  async function ct(gt) {
    const qe = (gt || "").trim();
    if (qe) {
      Et((Le) => [...Le, { role: "user", text: qe }]), ae(!0);
      try {
        const Le = { "Content-Type": "application/json" };
        j ? (Le["x-api-key"] = j, Le.Authorization = `Bearer ${j}`) : k && (Le.Authorization = `Bearer ${k}`), Te && (Le["X-Tenant-ID"] = Te);
        const it = `${at.current || "anon"}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
        Le["Idempotency-Key"] = it;
        const Qe = await (await fetch(`${I}/v1/chat/send`, {
          method: "POST",
          headers: Le,
          body: JSON.stringify({ message: qe, session_id: at.current })
        })).json();
        ae(!1), Et((He) => [...He, { role: "bot", text: Qe.text }]), Qe.session_id && Qe.session_id !== at.current && (at.current = Qe.session_id, localStorage.setItem("session_id", Qe.session_id)), Qe.options ? ce(Qe.options) : ce([]);
      } catch {
        ae(!1), Et((it) => [
          ...it,
          { role: "bot", text: (Ee == null ? void 0 : Ee.errorMessage) || "No pude responder. Intenta de nuevo." }
        ]), ce([]);
      }
    }
  }
  return /* @__PURE__ */ jt.jsxs("div", { className: "chat-container", "data-theme": Fe, children: [
    /* @__PURE__ */ jt.jsx(
      lk,
      {
        title: (Ee == null ? void 0 : Ee.headerTitle) || "Chat",
        subtitle: Ee == null ? void 0 : Ee.headerSubtitle,
        status: Ee == null ? void 0 : Ee.status
      }
    ),
    /* @__PURE__ */ jt.jsxs("div", { className: "chat-messages", ref: Ve, children: [
      /* @__PURE__ */ jt.jsx(ok, { messages: S }),
      Se && /* @__PURE__ */ jt.jsx(fk, {}),
      se.length > 0 && /* @__PURE__ */ jt.jsx(sk, { options: se, onSelect: (gt) => ct(gt.id) })
    ] }),
    /* @__PURE__ */ jt.jsx(
      ck,
      {
        value: tt,
        onChange: J,
        strings: Ee,
        onSend: () => {
          ct(tt), J("");
        }
      }
    )
  ] });
}
function pk({ apiUrl: I, apiKey: j, tenantId: k, tenantTheme: Te, strings: Fe, onClose: Ee }) {
  return /* @__PURE__ */ jt.jsx("div", { className: "chat-window-wrapper", children: /* @__PURE__ */ jt.jsxs("div", { className: "chat-window", "data-theme": Te, children: [
    /* @__PURE__ */ jt.jsx(
      "button",
      {
        className: "chat-close",
        onClick: Ee,
        "aria-label": (Fe == null ? void 0 : Fe.closeLabel) || "Cerrar chat",
        title: (Fe == null ? void 0 : Fe.closeLabel) || "Cerrar chat",
        children: "✕"
      }
    ),
    /* @__PURE__ */ jt.jsx(dk, { apiUrl: I, apiKey: j, tenantId: k, tenantTheme: Te, strings: Fe })
  ] }) });
}
function vk({ apiUrl: I, apiKey: j, tenantId: k, tenantTheme: Te, startOpen: Fe, strings: Ee }) {
  const [S, Et] = Ya.useState(!!Fe);
  return /* @__PURE__ */ jt.jsxs(jt.Fragment, { children: [
    !S && /* @__PURE__ */ jt.jsx(
      "button",
      {
        className: "floating-button",
        onClick: () => Et(!0),
        "aria-label": (Ee == null ? void 0 : Ee.openLabel) || "Abrir chat",
        title: (Ee == null ? void 0 : Ee.openLabel) || "Abrir chat",
        children: "💬"
      }
    ),
    S && /* @__PURE__ */ jt.jsx(
      pk,
      {
        apiUrl: I,
        apiKey: j,
        tenantId: k,
        tenantTheme: Te,
        strings: Ee,
        onClose: () => Et(!1)
      }
    )
  ] });
}
const iT = {
  es: {
    headerTitle: "Asistente virtual",
    headerSubtitle: "Resolvemos tus dudas",
    status: { label: "En linea" },
    openLabel: "Abrir chat",
    closeLabel: "Cerrar chat",
    messagePlaceholder: "Escribe un mensaje...",
    sendLabel: "Enviar",
    errorMessage: "No pude responder. Intenta de nuevo."
  },
  en: {
    headerTitle: "Virtual assistant",
    headerSubtitle: "We can help you",
    status: { label: "Online" },
    openLabel: "Open chat",
    closeLabel: "Close chat",
    messagePlaceholder: "Type a message...",
    sendLabel: "Send",
    errorMessage: "I could not reply. Please try again."
  }
};
function oT(I) {
  const j = (I || "").toLowerCase();
  return j.startsWith("en") ? "en" : (j.startsWith("es"), "es");
}
function hk(I) {
  const j = oT(I);
  return iT[j] || iT.es;
}
const mk = {
  tenantTheme: void 0,
  language: "es",
  startOpen: !1,
  apiKey: void 0,
  tenantId: void 0,
  headerTitle: void 0,
  headerSubtitle: void 0,
  widgetToken: void 0
};
function yk(I = {}) {
  const k = { ...mk, ...I && typeof I == "object" ? I : {} };
  return k.language = oT(k.language), k.startOpen = !!k.startOpen, k.apiKey && typeof k.apiKey == "string" ? k.apiKey = k.apiKey.trim() : k.apiKey = void 0, k.tenantId && typeof k.tenantId == "string" ? k.tenantId = k.tenantId.trim() : k.tenantId = void 0, k.widgetToken && typeof k.widgetToken == "string" ? k.widgetToken = k.widgetToken.trim() : k.widgetToken = void 0, k;
}
async function gk(I, j, k) {
  if (!k) return null;
  try {
    const Te = {};
    j && (Te.Authorization = `Bearer ${j}`, Te["x-api-key"] = j), Te["Idempotency-Key"] = `${k}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const Fe = await fetch(`${I}/v1/tenant/config`, { headers: Te });
    return Fe.ok ? await Fe.json() : null;
  } catch (Te) {
    return console.error("ChatWidget: no se pudo obtener la config del tenant", Te), null;
  }
}
window.ChatWidget = {
  init: async (I = {}) => {
    var Ee, S;
    const j = yk(I);
    if (!j.apiUrl) {
      console.error("ChatWidget: apiUrl es obligatorio");
      return;
    }
    const k = document.getElementById("widget-root");
    if (!k) {
      console.error("ChatWidget: no se encontró el elemento #widget-root");
      return;
    }
    const Te = await gk(j.apiUrl, j.apiKey, j.tenantId);
    Te && (!j.tenantTheme && Te.theme && (j.tenantTheme = Te.theme), !I.language && Te.language && (j.language = Te.language), !j.headerTitle && ((Ee = Te.texts) != null && Ee.header_title) && (j.headerTitle = Te.texts.header_title), !j.headerSubtitle && ((S = Te.texts) != null && S.header_subtitle) && (j.headerSubtitle = Te.texts.header_subtitle));
    const Fe = hk(j.language);
    vE(k).render(
      /* @__PURE__ */ jt.jsx(Z_.StrictMode, { children: /* @__PURE__ */ jt.jsx(
        vk,
        {
          apiUrl: j.apiUrl,
          apiKey: j.apiKey,
          widgetToken: j.widgetToken,
          tenantId: j.tenantId,
          tenantTheme: j.tenantTheme,
          startOpen: j.startOpen,
          strings: { ...Fe, headerTitle: j.headerTitle, headerSubtitle: j.headerSubtitle }
        }
      ) })
    );
  }
};
